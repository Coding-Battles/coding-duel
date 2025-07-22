import asyncpg
import asyncio
import os
import re
from typing import List
from groq import Groq

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_HOST = os.getenv("DATABASE_HOST", "188.245.96.146")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = Groq(api_key=GROQ_API_KEY)

# Username pool for instant access
username_pool = []
POOL_SIZE = 100
MIN_POOL_SIZE = 15
pool_lock = asyncio.Lock()


async def get_all_usernames() -> List[str]:
    """Fetch all usernames from the database."""

    # Database connection using environment variables
    conn = await asyncpg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
    )

    try:
        # Query to get all non-null usernames
        query = "SELECT username FROM \"user\" WHERE username IS NOT NULL AND username != ''"
        rows = await conn.fetch(query)
        usernames = [row["username"] for row in rows]
        return usernames
    finally:
        await conn.close()


async def is_username_taken(username: str) -> bool:
    """Check if username already exists in database."""

    conn = await asyncpg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
    )

    try:
        # Query to check if username exists (case-insensitive)
        query = 'SELECT COUNT(*) FROM "user" WHERE LOWER(username) = LOWER($1)'
        count = await conn.fetchval(query, username)
        return count > 0
    finally:
        await conn.close()


async def get_next_available_username(base_username: str) -> str:
    """Get the next available username by adding sequential numbers if needed."""

    # First try the base username without any numbers
    if not await is_username_taken(base_username):
        return base_username

    # Try username1, username2, username3, etc. until we find an available one
    for i in range(1, 10000):
        variant = f"{base_username}{i}"
        if not await is_username_taken(variant):
            return variant

    # If somehow all 9999 variants are taken, raise an exception
    raise Exception(f"No available username variants found for '{base_username}'")


async def generate_ai_username(count: int = 1) -> List[str]:
    """Generate creative usernames using Groq AI, ensuring they're available."""
    try:
        # Generate usernames using Groq API with minimal token usage
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": f"Generate {count} creative gaming usernames. Return ONLY the usernames, one per line. Do not number them. Do not add descriptions. Just the usernames.",
                },
                {"role": "user", "content": f"Generate {count} cool gaming usernames"},
            ],
            temperature=0.8,
            max_tokens=50 * count,  # Scale token limit with count
            top_p=1,
            stream=False,
            stop=None,
        )

        # Extract and clean the generated usernames
        generated_text = completion.choices[0].message.content.strip()
        generated_usernames = []

        for username in generated_text.split("\n"):
            if username.strip():
                # Remove number prefixes like "1. ", "2. ", etc.
                clean_username = re.sub(r"^\d+\.\s*", "", username.strip())
                # Remove quotes and other unwanted characters
                clean_username = (
                    clean_username.replace('"', "").replace("'", "").strip()
                )
                # Remove any remaining numbering patterns
                clean_username = re.sub(r"^\d+[\.\)\-\s]+", "", clean_username)

                if clean_username:
                    generated_usernames.append(clean_username)

        # Return only the AI-generated usernames (no fallback)
        if generated_usernames:
            available_usernames = await batch_get_available_usernames(generated_usernames)
            return available_usernames
        else:
            return []

    except Exception as e:
        # Log the error but don't use fallback
        print(f"AI username generation failed: {e}")
        return []


async def batch_check_usernames_availability(usernames: List[str]) -> dict[str, bool]:
    """Check availability of multiple usernames in a single database query."""
    if not usernames:
        return {}

    conn = await asyncpg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
    )

    try:
        # Check all usernames in one query using ANY (case-insensitive)
        # Convert usernames to lowercase for comparison
        lowercase_usernames = [username.lower() for username in usernames]
        query = 'SELECT username FROM "user" WHERE LOWER(username) = ANY($1)'
        taken_usernames = await conn.fetch(query, lowercase_usernames)
        taken_set = {row["username"].lower() for row in taken_usernames}

        # Return availability dict (case-insensitive comparison)
        return {username: username.lower() not in taken_set for username in usernames}
    finally:
        await conn.close()


async def batch_get_available_usernames(usernames: List[str]) -> List[str]:
    """Get available versions of multiple usernames efficiently."""
    if not usernames:
        return []

    conn = await asyncpg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
    )

    try:
        available_usernames = []

        # First check which base usernames are available
        availability = await batch_check_usernames_availability_with_connection(
            usernames, conn
        )

        for username in usernames:
            if availability[username]:
                # Base username is available
                available_usernames.append(username)
            else:
                # Find next available numbered version
                available_version = await find_next_available_numbered_username(
                    username, conn
                )
                available_usernames.append(available_version)

        return available_usernames
    finally:
        await conn.close()


async def batch_check_usernames_availability_with_connection(
    usernames: List[str], conn
) -> dict[str, bool]:
    """Check availability using existing connection."""
    if not usernames:
        return {}

    # Convert usernames to lowercase for comparison
    lowercase_usernames = [username.lower() for username in usernames]
    query = 'SELECT username FROM "user" WHERE LOWER(username) = ANY($1)'
    taken_usernames = await conn.fetch(query, lowercase_usernames)
    taken_set = {row["username"].lower() for row in taken_usernames}

    return {username: username.lower() not in taken_set for username in usernames}


async def find_next_available_numbered_username(base_username: str, conn) -> str:
    """Find next available numbered version using existing connection."""
    for i in range(1, 10000):
        variant = f"{base_username}{i}"
        query = 'SELECT COUNT(*) FROM "user" WHERE LOWER(username) = LOWER($1)'
        count = await conn.fetchval(query, variant)
        if count == 0:
            return variant

    # Fallback if somehow all are taken
    raise Exception(f"No available username variants found for '{base_username}'")


async def refill_username_pool():
    """Refill the username pool with fresh AI-generated usernames."""
    global username_pool

    async with pool_lock:
        try:
            # Only refill if pool is low
            if len(username_pool) >= MIN_POOL_SIZE:
                return

            print(f"Refilling username pool... Current size: {len(username_pool)}")

            # Generate usernames to fill the pool
            needed = POOL_SIZE - len(username_pool)
            new_usernames = await generate_ai_username(needed)
            username_pool.extend(new_usernames)

            print(f"Pool refilled! New size: {len(username_pool)}")

        except Exception as e:
            print(f"Error refilling username pool: {e}")


async def get_instant_username() -> str:
    """Get a username instantly from the pool."""
    global username_pool

    async with pool_lock:
        # If pool is empty, generate one on demand
        if not username_pool:
            print("Username pool empty, generating on demand...")
            usernames = await generate_ai_username(1)
            if not usernames:
                raise Exception("AI username generation failed and no fallback available")
            return usernames[0]

        # Get username from pool
        username = username_pool.pop(0)

        # Trigger background refill if running low
        if len(username_pool) < MIN_POOL_SIZE:
            asyncio.create_task(refill_username_pool())

        return username


async def initialize_username_pool():
    """Initialize the username pool on startup."""
    print("Initializing username pool...")
    await refill_username_pool()
    print("Username pool initialized!")


# Test functions - for development/testing purposes
async def test_all_functions():
    """Test all username functions"""
    print("🧪 Testing Username Functions\n")

    # Test 1: Get all usernames
    print("1. Getting all existing usernames...")
    usernames = await get_all_usernames()
    print(f"   Found {len(usernames)} usernames: {usernames}\n")

    # Test 2: Check if username is taken
    test_username = "testuser123"
    print(f"2. Checking if '{test_username}' is taken...")
    is_taken = await is_username_taken(test_username)
    print(f"   Result: {'Taken' if is_taken else 'Available'}\n")

    # Test 3: Get next available username
    print(f"3. Getting next available username for '{test_username}'...")
    available = await get_next_available_username(test_username)
    print(f"   Result: '{available}'\n")

    # Test 4: Generate AI username (single)
    print("4. Generating AI username...")
    ai_username = await generate_ai_username(1)
    print(f"   Generated: {ai_username}\n")

    # Test 5: Generate multiple AI usernames
    print("5. Generating 3 AI usernames...")
    ai_usernames = await generate_ai_username(3)
    print(f"   Generated: {ai_usernames}\n")

    print("✅ All tests completed!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_all_functions())
