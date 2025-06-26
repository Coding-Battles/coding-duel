'use client';


import { Session, User } from "better-auth";
import { createContext, useContext } from "react";

const SessionContext = createContext<User | null>(null);

export const SessionProvider = ({
  sessionUser,
  children,
}: {
  sessionUser: User | null;
  children: React.ReactNode;
}) => {
  return (
    <SessionContext.Provider value={sessionUser}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSessionContext = () => useContext(SessionContext);
