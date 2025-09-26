import java.util.*;
import java.lang.reflect.*;


// VersionControl API for first-bad-version problem
class VersionControl {
    private static int badVersion = 0;
    
    public static void setBadVersion(int bad) {
        badVersion = bad;
    }
    
    public static boolean isBadVersion(int version) {
        return version >= badVersion;
    }
}

java
