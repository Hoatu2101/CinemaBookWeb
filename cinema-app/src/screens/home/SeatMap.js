import React, { useState, useEffect, useContext } from "react";
import { Container, Button, Badge, Row, Col } from "react-bootstrap";
import Apis, { authApis, endpoints } from "../../configs/Apis";
import { MyUserContext } from "../../configs/context";
import { 
    lockSeatInFirebase, 
    unlockSeatInFirebase, 
    bookSeatsInFirebase, 
    listenShowtimeSeats 
} from "../../configs/firebase";
import "../../styles/SeatMap.css";
import cookies from "react-cookies";

const SeatMap = ({ showtimeId }) => {
    const [user] = useContext(MyUserContext);
    const [seats, setSeats] = useState([]);
    const [selectedSeats, setSelectedSeats] = useState([]);
    const [fbSeats, setFbSeats] = useState({});
    const [, setLoading] = useState(true);
    const [timeLeft, setTimeLeft] = useState(300); // 5 phút = 300 giây

    // Loại vé động kết nối với Backend Django DB (Giá chuẩn 75.000 VNĐ)
    const [ticketTypes, setTicketTypes] = useState([
        { id: 'adult_single', name: 'NGƯỜI LỚN', type: 'ĐƠN', price: 75000 },
        { id: 'student_single', name: 'HSSV-U22-GV', type: 'ĐƠN', price: 55000 },
        { id: 'senior_single', name: 'NGƯỜI CAO TUỔI', type: 'ĐƠN', price: 55000 },
        { id: 'adult_couple', name: 'NGƯỜI LỚN', type: 'ĐÔI', price: 140000 },
    ]);

    const [ticketCounts, setTicketCounts] = useState({
        adult_single: 1, // Mặc định 1 vé người lớn
        student_single: 0,
        senior_single: 0,
        adult_couple: 0
    });

    const totalTicketsCount = Object.values(ticketCounts).reduce((a, b) => a + b, 0);
    const totalPrice = ticketTypes.reduce((sum, item) => sum + (ticketCounts[item.id] || 0) * (item.price || 75000), 0);
    const validId = showtimeId && typeof showtimeId === 'object' ? showtimeId.id : showtimeId;

    let clientSessionId = sessionStorage.getItem("client_session_id");
    if (!clientSessionId) {
        clientSessionId = "sess_" + Math.random().toString(36).substring(2, 9) + "_" + Date.now();
        sessionStorage.setItem("client_session_id", clientSessionId);
    }
    const currentUser = user || cookies.load("user") || { username: "khachhang" };
    const myLockUserId = currentUser?.id ? `user_${currentUser.id}` : ((currentUser?.username && currentUser.username !== "khachhang") ? `user_${currentUser.username}` : clientSessionId);
    const lockUserObject = { ...currentUser, lock_user_id: myLockUserId };

    // Tải danh sách Loại Vé thực tế từ Backend Django
    useEffect(() => {
        const fetchTicketTypes = async () => {
            try {
                const typeEndpoint = endpoints.type_tickets || "/type-tickets/";
                const res = await Apis.get(typeEndpoint);
                const list = Array.isArray(res.data) ? res.data : (res.data?.results || []);
                if (list.length > 0) {
                    const formatted = list.map((item) => ({
                        id: `backend_${item.id}`,
                        name: item.name ? item.name.toUpperCase() : "VÉ XEM PHIM",
                        type: item.name && item.name.toLowerCase().includes("đôi") ? "ĐÔI" : "ĐƠN",
                        price: item.price || 75000
                    }));
                    setTicketTypes(formatted);
                    
                    const initialCounts = {};
                    formatted.forEach((t, idx) => {
                        initialCounts[t.id] = idx === 0 ? 1 : 0;
                    });
                    setTicketCounts(initialCounts);
                }
            } catch (err) {
                console.warn("Dùng danh sách loại vé mặc định (Giá 75k):", err);
            }
        };

        fetchTicketTypes();
    }, []);

    // 1. Tải danh sách ghế từ backend Django
    useEffect(() => {
        const fetchSeats = async () => {
            if (!validId || validId === "[object Object]") {
                console.warn("SeatMap: showtimeId chưa hợp lệ hoặc chưa được chọn.");
                setLoading(false);
                setSeats([]);
                setFbSeats({});
                setSelectedSeats([]);
                return;
            }

            setLoading(true);
            setSeats([]); // Reset seats state để không bị dính trạng thái ghế của suất chiếu cũ
            setFbSeats({}); // Reset firebase state khi đổi suất chiếu
            setSelectedSeats([]); // Reset danh sách ghế đang chọn
            try {
                const seatEndpoint = endpoints.seats ? endpoints.seats(validId) : `/showtimes/${validId}/seats/`;
                let res = await Apis.get(seatEndpoint);
                const seatList = Array.isArray(res.data) ? res.data : (res.data?.seats || []);
                setSeats(seatList);
            } catch (err) {
                console.error("Lỗi tải sơ đồ ghế:", err);
                setSeats([]);
            } finally {
                setLoading(false);
            }
        };

        fetchSeats();

        // Tự động polling làm tươi dữ liệu ghế từ Backend mỗi 2.5 giây để luôn đồng bộ tức thì giữa các thiết bị
        const pollInterval = setInterval(async () => {
            if (!validId || validId === "[object Object]") return;
            try {
                const seatEndpoint = endpoints.seats ? endpoints.seats(validId) : `/showtimes/${validId}/seats/`;
                let res = await Apis.get(seatEndpoint);
                const seatList = Array.isArray(res.data) ? res.data : (res.data?.seats || []);
                if (seatList.length > 0) {
                    setSeats(seatList);
                }
            } catch (err) {}
        }, 2500);

        return () => clearInterval(pollInterval);
    }, [showtimeId, validId]);

    // 2. Lắng nghe trạng thái ghế Realtime trên Firebase theo đúng suất chiếu (showtimeId)
    useEffect(() => {
        if (!validId) {
            setFbSeats({});
            return;
        }

        setFbSeats({}); // Reset trạng thái Firebase cũ ngay lập tức khi đổi suất chiếu
        const unsubscribe = listenShowtimeSeats(validId, (realtimeData) => {
            setFbSeats(realtimeData || {});
        });

        return () => {
            setFbSeats({});
            unsubscribe();
        };
    }, [validId]);

    // 3. Đếm ngược 5 phút giữ ghế tạm thời
    useEffect(() => {
        if (selectedSeats.length === 0) {
            setTimeLeft(300);
            return;
        }

        const timer = setInterval(() => {
            setTimeLeft((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    const expiredSeatIds = selectedSeats.map((s) => s.id || s.seatId);
                    expiredSeatIds.forEach((sId) => {
                        unlockSeatInFirebase(validId, sId);
                    });
                    authApis().post("/seat-statuses/unlock_seats/", { showtime_id: validId, seat_ids: expiredSeatIds }).catch(() => {});
                    setSelectedSeats([]);
                    alert("Đã hết 5 phút giữ ghế! Ghế của bạn đã được tự động giải phóng về trạng thái ban đầu.");
                    return 300;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [selectedSeats, validId]);

    // Tăng số lượng vé theo loại
    const handleAddTicket = (typeId) => {
        if (totalTicketsCount >= 8) {
            alert("Bạn chỉ được đặt tối đa 8 vé cho mỗi lần giao dịch!");
            return;
        }
        setTicketCounts((prev) => ({
            ...prev,
            [typeId]: (prev[typeId] || 0) + 1
        }));
    };

    // Giảm số lượng vé theo loại
    const handleSubTicket = (typeId) => {
        if ((ticketCounts[typeId] || 0) <= 0) return;
        const newCounts = {
            ...ticketCounts,
            [typeId]: ticketCounts[typeId] - 1
        };
        const newTotal = Object.values(newCounts).reduce((a, b) => a + b, 0);

        if (newTotal === 0) {
            alert("Số lượng vé tổng cộng phải ít nhất là 1 vé!");
            return;
        }

        setTicketCounts(newCounts);

        if (selectedSeats.length > newTotal) {
            const excess = selectedSeats.slice(newTotal);
            excess.forEach(s => unlockSeatInFirebase(validId, s.id || s.seatId));
            setSelectedSeats(selectedSeats.slice(0, newTotal));
        }
    };

    // Xử lý khi nhấp chọn / hủy chọn ghế theo tổng số lượng vé đã chọn
    const handleSeatClick = (seat) => {
        const currentId = seat.id || seat.seatId;
        const fbSeat = fbSeats[currentId];

        const isBooked = seat.status === "BOOKED" || seat.status === "SOLD" || fbSeat?.status === "BOOKED";
        if (isBooked) {
            alert("Ghế này đã được khách hàng khác đặt mua!");
            return;
        }

        const isAlreadySelected = selectedSeats.some((s) => (s.id || s.seatId) === currentId);
        const isLockedByOthers = (fbSeat?.status === "LOCKED" && fbSeat?.user_id !== myLockUserId) ||
            (seat.status === "LOCKED" && !isAlreadySelected);

        if (isLockedByOthers) {
            alert("Ghế này đang được người khác giữ chỗ trong 5 phút! Vui lòng chọn ghế khác.");
            return;
        }

        if (isAlreadySelected) {
            setSelectedSeats((prev) => prev.filter((s) => (s.id || s.seatId) !== currentId));
            unlockSeatInFirebase(validId, currentId);
            try {
                const apiCaller = authApis ? authApis() : Apis;
                apiCaller.post("/seat-statuses/unlock_seats/", { showtime_id: validId, seat_ids: [currentId], client_session_id: myLockUserId }).catch(() => {});
            } catch (e) {}
        } else {
            let currentTotal = totalTicketsCount;
            if (currentTotal === 0) {
                const defaultKey = ticketTypes[0]?.id || "adult_single";
                setTicketCounts((prev) => ({ ...prev, [defaultKey]: 1 }));
                currentTotal = 1;
            } else if (selectedSeats.length >= currentTotal) {
                alert(`Bạn đã chọn đủ ${currentTotal} ghế tương ứng với ${currentTotal} vé! Hãy tăng số lượng vé ở bảng trên nếu muốn chọn thêm ghế.`);
                return;
            }

            setSelectedSeats((prev) => [...prev, seat]);
            setTimeLeft(300);
            lockSeatInFirebase(validId, currentId, lockUserObject);
            try {
                const apiCaller = authApis ? authApis() : Apis;
                apiCaller.post("/seat-statuses/lock_seats/", { showtime_id: validId, seat_ids: [currentId], client_session_id: myLockUserId }).catch(() => {});
            } catch (e) {}
        }
    };

    const groupSeatsByRow = () => {
        const rows = {};
        if (!Array.isArray(seats)) return rows;

        seats.forEach((seat) => {
            const seatName = seat.seat_number || seat.name || seat.seatNumber || "";
            const rowLetter = seatName ? seatName.charAt(0).toUpperCase() : "?";
            if (!rows[rowLetter]) {
                rows[rowLetter] = [];
            }
            rows[rowLetter].push(seat);
        });

        Object.keys(rows).forEach((rowKey) => {
            rows[rowKey].sort((a, b) => {
                const nameA = a.seat_number || a.name || a.seatNumber || "";
                const nameB = b.seat_number || b.name || b.seatNumber || "";
                const numA = parseInt(nameA?.substring(1)) || 0;
                const numB = parseInt(nameB?.substring(1)) || 0;
                return numA - numB;
            });
        });

        return rows;
    };

    const seatRows = groupSeatsByRow();

    const formatCountdown = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    // Xử lý Thanh Toán VNPay Sandbox hoặc Tiền Mặt
    const handleCheckout = async () => {
        if (selectedSeats.length === 0) {
            alert("Vui lòng chọn ghế trên sơ đồ!");
            return;
        }

        if (selectedSeats.length < totalTicketsCount) {
            alert(`Bạn đã đăng ký ${totalTicketsCount} vé nhưng mới chọn ${selectedSeats.length} ghế. Vui lòng chọn đủ ${totalTicketsCount} ghế trên sơ đồ trước khi thanh toán!`);
            return;
        }

        const token = cookies.load("token");
        if (!token) {
            alert("Vui lòng đăng nhập để tiếp tục đặt vé!");
            return;
        }

        const seatIds = selectedSeats.map(s => s.id || s.seatId);
        const bookingData = {
            showtime: validId,
            showtime_id: validId,
            payment_method: "VNPAY",
            seat_ids: seatIds
        };

        try {
            console.log("Đang tiến hành tạo đơn vé thanh toán online:", bookingData);

            const bookingEndpoint = endpoints.booking || "/bookings/";
            const res = await authApis().post(bookingEndpoint, bookingData);

            if (res.status === 200 || res.status === 201) {
                const orderId = res.data?.id || res.data;

                try {
                    const vnpayRes = await authApis().post(`/bookings/${orderId}/create_vnpay_url/`);
                    if (vnpayRes.data?.payment_url) {
                        window.location.href = vnpayRes.data.payment_url;
                        return;
                    }
                } catch (vnpErr) {
                    console.error("Lỗi khởi tạo cổng VNPay:", vnpErr);
                    alert("Không thể khởi tạo cổng thanh toán VNPay: " + (vnpErr.response?.data?.error || vnpErr.message));
                    return;
                }

                await bookSeatsInFirebase(validId, seatIds, lockUserObject);
                alert(`Đặt vé thành công! Mã đơn vé của bạn là: #${orderId}`);
                setSelectedSeats([]);

                const seatEndpoint = endpoints.seats ? endpoints.seats(validId) : `/showtimes/${validId}/seats/`;
                const reload = await Apis.get(seatEndpoint);
                const seatList = Array.isArray(reload.data) ? reload.data : (reload.data?.seats || []);
                setSeats(seatList);
            }
        } catch (err) {
            console.error("Chi tiết lỗi đặt vé:", err.response?.data || err.message);
            if (err.response) {
                const status = err.response.status;
                if (status === 401 || status === 403 || status === 302) {
                    alert("Tài khoản chưa được xác thực hoặc phiên đăng nhập đã hết hạn!");
                } else if (status === 400) {
                    const data = err.response.data;
                    let errorMsg = "Dữ liệu đặt vé không hợp lệ.";
                    if (typeof data === 'string') {
                        errorMsg = data;
                    } else if (data && typeof data === 'object') {
                        errorMsg = data.error || data.message || data.detail || Object.values(data).flat().join(", ");
                    }
                    alert("Lỗi đặt vé: " + errorMsg);
                } else {
                    alert("Hệ thống đang bận hoặc gặp sự cố, xin thử lại sau.");
                }
            } else {
                alert("Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại mạng!");
            }
        }
    };

    return (
        <Container className="seatmap-container my-5 p-4 rounded shadow-lg" style={{ backgroundColor: "#14141d", border: "1px solid #dc2626" }}>
            <h3 className="text-center text-white mb-4 fw-bold">CHỌN LOẠI VÉ & GHẾ NGỒI</h3>

            {/* DANH SÁCH THẺ CHỌN LOẠI VÉ KẾT NỐI VỚI BACKEND DJANGO */}
            <div className="mb-4">
                <Row className="g-3">
                    {ticketTypes.map((item) => {
                        const count = ticketCounts[item.id] || 0;
                        return (
                            <Col key={item.id} xs={12} sm={6} md={3}>
                                <div 
                                    className="p-3 rounded border text-start" 
                                    style={{ 
                                        backgroundColor: "#191838", 
                                        borderColor: count > 0 ? "#8b5cf6" : "#2f2d5a",
                                        boxShadow: count > 0 ? "0 0 12px rgba(139, 92, 246, 0.4)" : "none"
                                    }}
                                >
                                    <div className="fw-bold text-white mb-1" style={{ fontSize: "0.95rem", letterSpacing: "0.5px" }}>
                                        {item.name}
                                    </div>
                                    <div className="fw-bold mb-2" style={{ color: "#f5e625", fontSize: "0.85rem" }}>
                                        {item.type}
                                    </div>
                                    <div className="fw-bold text-white mb-3" style={{ fontSize: "1.05rem" }}>
                                        {(item.price || 75000).toLocaleString("vi-VN")} VNĐ
                                    </div>

                                    {/* Nút bấm Stepper [- N +] */}
                                    <div className="d-inline-flex align-items-center rounded overflow-hidden" style={{ backgroundColor: "#2b2b48" }}>
                                        <button 
                                            type="button"
                                            className="btn btn-sm text-white px-3 py-1 border-0 fw-bold" 
                                            style={{ backgroundColor: "transparent" }}
                                            onClick={() => handleSubTicket(item.id)}
                                        >
                                            -
                                        </button>
                                        <span className="text-white fw-bold px-3 py-1" style={{ minWidth: "32px", textAlign: "center" }}>
                                            {count}
                                        </span>
                                        <button 
                                            type="button"
                                            className="btn btn-sm text-white px-3 py-1 border-0 fw-bold" 
                                            style={{ backgroundColor: "transparent" }}
                                            onClick={() => handleAddTicket(item.id)}
                                        >
                                            +
                                        </button>
                                    </div>
                                </div>
                            </Col>
                        );
                    })}
                </Row>
                
                {/* Dòng thông báo hướng dẫn chọn đủ số lượng ghế */}
                <div className="text-center mt-3">
                    <Badge bg="warning" text="dark" className="px-3 py-2 fs-6 fw-bold">
                        Vui lòng chọn {totalTicketsCount} ghế trên sơ đồ bên dưới (Đã chọn {selectedSeats.length}/{totalTicketsCount} ghế)
                    </Badge>
                </div>
            </div>

            {/* Đồng hồ đếm ngược 5 phút giữ ghế */}
            {selectedSeats.length > 0 && (
                <div className="text-center mb-4">
                    <Badge bg="danger" className="px-3 py-2 fs-6 fw-bold">
                        Thời gian giữ ghế tạm thời (5 phút): {formatCountdown(timeLeft)}
                    </Badge>
                </div>
            )}

            {/* Chú thích loại ghế */}
            <div className="seat-legend d-flex justify-content-center flex-wrap gap-4 mb-5">
                <div className="legend-item d-flex align-items-center gap-2">
                    <div className="seat-icon available" style={{ backgroundColor: "#4b4b8f" }}></div> <span className="text-white">Ghế trống</span>
                </div>
                <div className="legend-item d-flex align-items-center gap-2">
                    <div className="seat-icon selected" style={{ backgroundColor: "#f5e625" }}></div> <span className="text-white">Đang chọn ({selectedSeats.length}/{totalTicketsCount} ghế)</span>
                </div>
                <div className="legend-item d-flex align-items-center gap-2">
                    <div className="seat-icon holding" style={{ backgroundColor: "#f97316", width: "24px", height: "24px", borderRadius: "4px" }}></div> <span className="text-white">Đang giữ (5 phút)</span>
                </div>
                <div className="legend-item d-flex align-items-center gap-2">
                    <div className="seat-icon booked" style={{ backgroundColor: "#333333" }}></div> <span className="text-white">Đã bán</span>
                </div>
            </div>

            {/* Màn hình chiếu */}
            <div className="screen-container text-center mb-5">
                <div className="cinema-screen"></div>
                <p className="text-muted mt-3 fw-bold" style={{ letterSpacing: "5px", fontSize: "0.9rem" }}>MÀN HÌNH</p>
            </div>

            {/* Sơ đồ ghế Realtime Firebase */}
            <div className="seats-grid d-flex flex-column align-items-center mb-4">
                {Object.keys(seatRows).length > 0 ? (
                    Object.keys(seatRows).sort().map((rowKey) => (
                        <div key={rowKey} className="seat-row d-flex align-items-center mb-3">
                            <div className="row-label me-3 text-center">
                                <span className="badge bg-danger text-white fw-bold px-2 py-1 fs-6">Hàng {rowKey}</span>
                            </div>

                            <div className="d-flex gap-2 flex-nowrap align-items-center justify-content-center">
                                {seatRows[rowKey].map((seat) => {
                                    const currentId = seat.id || seat.seatId;
                                    const seatName = seat.seat_number || seat.name || seat.seatNumber || "";

                                    const fbSeat = fbSeats[currentId];
                                    const isBooked = seat.status === "BOOKED" || seat.status === "SOLD" || fbSeat?.status === "BOOKED";
                                    const isSelectedByMe = selectedSeats.some((s) => (s.id || s.seatId) === currentId);
                                    const isLockedByOthers = (fbSeat?.status === "LOCKED" && fbSeat?.user_id !== myLockUserId) ||
                                        (seat.status === "LOCKED" && !isSelectedByMe);

                                    let seatClass = "available";
                                    let seatStyle = { minWidth: "42px", height: "42px", fontSize: "0.85rem", cursor: "pointer" };

                                    if (isBooked) {
                                        seatClass = "booked";
                                        seatStyle.backgroundColor = "#333333";
                                        seatStyle.color = "#666666";
                                        seatStyle.cursor = "not-allowed";
                                    } else if (isLockedByOthers) {
                                        seatClass = "holding";
                                        seatStyle.backgroundColor = "#f97316";
                                        seatStyle.color = "#ffffff";
                                        seatStyle.cursor = "not-allowed";
                                    } else if (isSelectedByMe) {
                                        seatClass = "selected";
                                        seatStyle.backgroundColor = "#f5e625";
                                        seatStyle.color = "#111111";
                                    } else {
                                        seatStyle.backgroundColor = "#4b4b8f";
                                        seatStyle.color = "#ffffff";
                                    }

                                    return (
                                        <div
                                            key={currentId}
                                            className={`seat-box d-flex align-items-center justify-content-center rounded ${seatClass}`}
                                            onClick={() => handleSeatClick(seat)}
                                            title={isBooked ? `Ghế ${seatName} (Đã bán)` : isLockedByOthers ? `Ghế ${seatName} (Đang giữ chỗ 5 phút)` : `Ghế ${seatName}`}
                                            style={seatStyle}
                                        >
                                            <span className="seat-number fw-bold">
                                                {seatName}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>

                            <div className="row-label ms-3 text-center">
                                <span className="badge bg-danger text-white fw-bold px-2 py-1 fs-6">Hàng {rowKey}</span>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-4 border border-secondary border-dashed rounded w-100" style={{ maxWidth: "500px", color: "#8a8a8a" }}>
                        <p className="mb-0 fw-medium">Chưa có dữ liệu sơ đồ ghế cho suất chiếu này.</p>
                    </div>
                )}
            </div>

            {/* Thanh thanh toán */}
            {selectedSeats.length > 0 && (
                <div className="checkout-bar mt-5 p-4 rounded shadow bg-black border border-danger">
                    <Row className="align-items-center">
                        <Col md={7}>
                            <p className="mb-1 text-light fs-5">
                                Ghế chọn ({selectedSeats.length}/{totalTicketsCount} ghế): <span className="text-warning fw-bold">{selectedSeats.map(s => s.seat_number || s.name || s.seatNumber).join(", ")}</span>
                            </p>
                            <h3 className="text-danger fw-bold mb-3 d-flex align-items-center gap-2 flex-wrap">
                                <span>Tổng cộng: {totalPrice.toLocaleString("vi-VN")} đ</span>
                                <small className="text-warning fs-6 font-monospace border border-warning px-2 py-1 rounded" style={{ backgroundColor: "rgba(245, 230, 37, 0.1)" }}>
                                    ({ticketTypes.filter(t => (ticketCounts[t.id] || 0) > 0).map(t => `${ticketCounts[t.id]}x ${t.name}`).join(" + ")})
                                </small>
                            </h3>

                            {/* Phương thức Thanh toán Duy nhất: Online qua VNPay */}
                            <div className="d-flex align-items-center gap-3">
                                <span className="text-white fw-semibold">Phương thức thanh toán:</span>
                                <div className="d-inline-flex align-items-center gap-2 bg-dark px-3 py-2 rounded border border-info">
                                    <Badge bg="info" className="text-dark font-monospace fs-6">ONLINE VNPAY</Badge>
                                    <span className="text-info fw-bold text-sm">Quét mã VNPay-QR / Thẻ ATM / Thẻ Quốc tế</span>
                                </div>
                            </div>
                        </Col>

                        <Col md={5} className="text-md-end mt-3 mt-md-0">
                            <Button 
                                variant="danger" 
                                size="lg" 
                                className="fw-bold px-5 py-3 text-uppercase" 
                                style={{ backgroundColor: "#dc2626", borderColor: "#dc2626", letterSpacing: "1px" }} 
                                onClick={handleCheckout}
                            >
                                Thanh toán
                            </Button>
                        </Col>
                    </Row>
                </div>
            )}
        </Container>
    );
};

export default SeatMap;