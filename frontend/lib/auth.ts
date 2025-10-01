import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  advanced: {
    cookiePrefix: "better-auth",
  },

  session: {
    expiresIn: 60 * 60 * 24 * 30, // 30 days
    updateAge: 60 * 60 * 24, // Update session every day
  },

  socialProviders: {
    google: {
      clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    },
  },


  user: {
    additionalFields: {
      username: {
        type: "string",
        required: false,
        unique: true,
      },
      selectedPfp: {
        type: "number",
        required: false,
        defaultValue: 0,
      },
      easylp: {
        type: "number",
        required: false,
        defaultValue: 0,
      },
      mediumlp: {
        type: "number",
        required: false,
        defaultValue: 0,
      },
      hardlp: {
        type: "number",
        required: false,
        defaultValue: 0,
      },
    },
  },

  plugins: [nextCookies()],
});
