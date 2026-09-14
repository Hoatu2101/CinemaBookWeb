import { initializeApp } from "firebase/app";
import { getDatabase, ref, onValue, set, remove } from "firebase/database";

// Cấu hình Firebase Project cinema-app-336e5
const firebaseConfig = {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyCMSQ_vnqbsFVfy8UXpH3HOtjzaczr-Xg0",
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "cinema-app-336e5.firebaseapp.com",
    databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL || "https://cinema-app-336e5-default-rtdb.firebaseio.com",
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "cinema-app-336e5",
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "cinema-app-336e5.firebasestorage.app",
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "175524675912",
    appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:175524675912:web:7783e163ae52422bab737d",
    measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID || "G-GBV3K7T9D2"
};

// Khởi tạo Firebase App duy nhất
const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);

// Thời gian giữ ghế 5 phút = 300.000 milliseconds
export const HOLD_TIME_MS = 5 * 60 * 1000;

/**
 * Khách hàng chọn ghế -> Khóa giữ ghế 5 phút trên Firebase Realtime Database
 */
export const lockSeatInFirebase = async (showtimeId, seatId, user) => {
    if (!showtimeId || !seatId) return;

    try {
        const seatRef = ref(db, `showtimes/${showtimeId}/seats/${seatId}`);
        const now = Date.now();
        const expiresAt = now + HOLD_TIME_MS;

        const seatData = {
            status: "LOCKED",
            user_id: user?.lock_user_id || user?.id || user?.username || "guest",
            username: user?.username || "khachhang",
            locked_at: now,
            expires_at: expiresAt
        };

        await set(seatRef, seatData);
        return expiresAt;
    } catch (err) {
        console.warn("Lỗi đồng bộ giữ ghế lên Firebase:", err);
    }
};
/**
 * Hủy giữ ghế -> Trả ghế về hiện trạng ban đầu (FREE)
 */
export const unlockSeatInFirebase = async (showtimeId, seatId) => {
    if (!showtimeId || !seatId) return;
    try {
        const seatRef = ref(db, `showtimes/${showtimeId}/seats/${seatId}`);
        await remove(seatRef);
    } catch (err) {
        console.warn("Lỗi mở lại ghế trên Firebase:", err);
    }
};
/**
 * Đặt vé & Thanh toán thành công -> Khóa vĩnh viễn (BOOKED) không cho ai ấn vào
 */
export const bookSeatsInFirebase = async (showtimeId, seatIds, user) => {
    if (!showtimeId || !Array.isArray(seatIds)) return;

    const now = Date.now();
    try {
        for (const seatId of seatIds) {
            const seatRef = ref(db, `showtimes/${showtimeId}/seats/${seatId}`);
            await set(seatRef, {
                status: "BOOKED",
                user_id: user?.id || user?.username || "guest",
                booked_at: now
            });
        }
    } catch (err) {
        console.warn("Lỗi cập nhật trạng thái BOOKED lên Firebase:", err);
    }
};

/**
 * Lắng nghe Realtime tất cả ghế theo Suất Chiếu
 * Tự động hủy giữ ghế khi vượt quá 5 phút
 */
export const listenShowtimeSeats = (showtimeId, onSeatChange) => {
    if (!showtimeId) return () => {};

    try {
        const seatsRef = ref(db, `showtimes/${showtimeId}/seats`);

        const unsubscribe = onValue(seatsRef, (snapshot) => {
            const val = snapshot.val() || {};
            const now = Date.now();
            const activeSeats = {};

            Object.keys(val).forEach((seatId) => {
                const item = val[seatId];
                
                // Nếu giữ ghế quá 5 phút chưa thanh toán -> Tự động giải phóng về trạng thái ban đầu
                if (item.status === "LOCKED" && item.expires_at && now > item.expires_at) {
                    unlockSeatInFirebase(showtimeId, seatId);
                } else {
                    activeSeats[seatId] = item;
                }
            });

            onSeatChange(activeSeats);
        }, (error) => {
            console.warn("Lỗi nghe dữ liệu Firebase Realtime:", error);
        });

        return unsubscribe;
    } catch (err) {
        console.warn("Khởi tạo listener Firebase thất bại:", err);
        return () => {};
    }
};
