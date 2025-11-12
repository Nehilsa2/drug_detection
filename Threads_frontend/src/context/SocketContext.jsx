// import { createContext, useContext, useEffect, useState } from "react";
// import { useRecoilValue } from "recoil";
// import io from "socket.io-client";
// import userAtom from "../atoms/userAtom";

// const SocketContext = createContext();

// export const useSocket = () => {
// 	return useContext(SocketContext);
// };

// export const SocketContextProvider = ({ children }) => {
// 	const [socket, setSocket] = useState(null);
// 	const [onlineUsers, setOnlineUsers] = useState([]);
// 	const user = useRecoilValue(userAtom);

// 	useEffect(() => {
// 		const socket = io("/", {
// 			query: {
// 				userId: user?._id,
// 			},
// 		});

// 		setSocket(socket);

// 		socket.on("getOnlineUsers", (users) => {
// 			setOnlineUsers(users);
// 		});
// 		return () => socket && socket.close();
// 	}, [user?._id]);

// 	return <SocketContext.Provider value={{ socket, onlineUsers }}>{children}</SocketContext.Provider>;
// };


import { createContext, useContext, useEffect, useState } from "react";
import { useRecoilValue } from "recoil";
import io from "socket.io-client";
import userAtom from "../atoms/userAtom";

const SocketContext = createContext();

export const useSocket = () => {
  return useContext(SocketContext);
};

export const SocketContextProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const user = useRecoilValue(userAtom);

  useEffect(() => {
    // ⚠️ Don't connect until the user is logged in
    if (!user?._id) return;

    // 🌐 Automatically switch URL based on environment
    const BACKEND_URL =
      import.meta.env.MODE === "production"
        ? "https://threads-backend-zi02.onrender.com" // your Render backend
        : "http://localhost:5000"; // your local backend port

    // ✅ Create socket connection
    const socketInstance = io(BACKEND_URL, {
      query: { userId: user._id },
      transports: ["websocket"], // ensure stable connection
    });

    setSocket(socketInstance);

    // ✅ Listen for online users
    socketInstance.on("getOnlineUsers", (users) => {
      setOnlineUsers(users);
    });

    // 🧹 Cleanup when user logs out / socket unmounts
    return () => socketInstance.close();
  }, [user?._id]);

  return (
    <SocketContext.Provider value={{ socket, onlineUsers }}>
      {children}
    </SocketContext.Provider>
  );
};

