import React, { useEffect, useState, useContext } from 'react';
import { Container, Card, Row, Col, Badge, Button } from 'react-bootstrap';
import { useLocation, Link } from 'react-router-dom';
import { authApis } from '../../configs/Apis';
import { MyUserContext } from '../../configs/context';
import { unlockSeatInFirebase, bookSeatsInFirebase } from '../../configs/firebase';
import cookies from 'react-cookies';

const VNPayReturn = () => {
    const [user] = useContext(MyUserContext);
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const status = queryParams.get('status');
    const bookingId = queryParams.get('booking_id') || queryParams.get('vnp_TxnRef');
    const showtimeId = queryParams.get('showtime_id');
    const rawSeatIds = queryParams.get('seat_ids');
    const isSuccess = status === 'success' || queryParams.get('vnp_ResponseCode') === '00';

    const [bookingData, setBookingData] = useState(null);
    const [, setLoading] = useState(true);

    const currentUser = user || cookies.load("user") || { username: "khachhang" };

    // Tải chi tiết đơn vé vừa thanh toán từ backend Django
    useEffect(() => {
        const fetchBooking = async () => {
            if (!bookingId || !isSuccess) {
                setLoading(false);
                return;
            }
            try {
                const res = await authApis().get(`/bookings/${bookingId}/`);
                setBookingData(res.data);
            } catch (err) {
                console.error("Lỗi khi tải chi tiết đơn vé:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchBooking();
    }, [bookingId, isSuccess]);

    // Tự động xử lý trạng thái ghế trên Firebase Realtime & Django DB khi nhận phản hồi từ VNPay
    useEffect(() => {
        if (!showtimeId || !rawSeatIds) return;

        const seatIdsArray = rawSeatIds.split(',').map(s => s.trim()).filter(Boolean);

        if (isSuccess) {
            // Thanh toán VNPay thành công -> Khóa vĩnh viễn ghế (BOOKED)
            bookSeatsInFirebase(showtimeId, seatIdsArray, currentUser);
        } else {
            // Hủy thanh toán VNPay hoặc thất bại -> Giải phóng toàn bộ ghế về hiện trạng ban đầu (FREE)
            seatIdsArray.forEach((seatId) => {
                unlockSeatInFirebase(showtimeId, seatId);
            });
            try {
                authApis().post('/seat-statuses/unlock_seats/', {
                    showtime_id: showtimeId,
                    seat_ids: seatIdsArray
                }).catch(() => {});
            } catch (e) {}
        }
    }, [isSuccess, showtimeId, rawSeatIds, currentUser]);

    // Hàm thực hiện In vé / Tải vé làm file PDF / Ảnh
    const handlePrintTicket = () => {
        window.print();
    };

    const ticketsList = bookingData?.tickets || [];
    const movieTitle = bookingData?.movie_title || "Phim chiếu rạp";
    const posterUrl = bookingData?.movie_poster || "https://res.cloudinary.com/dxxwcby8l/image/upload/v1717013892/Cinemax-Placeholder-Gold-Star_d3k4e0.jpg";
    const cinemaName = bookingData?.cinema_name || "Rạp CineBook Landmark 81";
    const roomName = bookingData?.room_name || "Phòng chiếu 01";
    const showDate = bookingData?.showtime_date || "";
    const showTime = bookingData?.showtime_time || "";

    return (
        <div style={{ backgroundColor: '#0d0d12', minHeight: '100vh', paddingTop: '40px', paddingBottom: '60px' }}>
            <Container className="text-white">
                {isSuccess ? (
                    <div>
                        <div className="text-center mb-4">
                            <Badge bg="success" className="px-4 py-2 fs-5 mb-2 text-uppercase">
                                ✅ THANH TOÁN THÀNH CÔNG
                            </Badge>
                            <h2 className="fw-bold text-white">CẢM ƠN BẠN ĐÃ ĐẶT VÉ TẠI CINEBOOK!</h2>
                            <p className="text-white opacity-75">
                                Mã đơn vé <strong style={{ color: '#ff4d4d' }}>#{bookingId}</strong> của bạn đã được xuất thành công. Bạn có thể in vé hoặc lưu lại mã QR dưới đây để soát vé tại rạp.
                            </p>
                        </div>

                        {/* HIỂN THỊ DANH SÁCH TẤT CẢ VÉ VỪA MUA (1 VÉ = 1 GHẾ) CÓ MÃ QR VÀ POSTER */}
                        <div className="d-flex flex-column gap-4 align-items-center">
                            {ticketsList.length > 0 ? (
                                ticketsList.map((ticket, idx) => {
                                    const ticketCode = ticket.ticket_code || `TK-${bookingId}-${idx + 1}`;
                                    const seatNumber = ticket.seat_number || ticket.seat?.seat_number || "Ghế đã chọn";
                                    const ticketPrice = ticket.price || (bookingData?.total_price / ticketsList.length) || 75000;

                                    return (
                                        <Card key={ticketCode} className="text-white border-danger shadow-lg overflow-hidden w-100 printable-ticket" style={{ maxWidth: '850px', backgroundColor: '#14141d', borderLeft: '8px solid #dc2626' }}>
                                            {/* Header Thẻ Vé */}
                                            <Card.Header className="d-flex justify-content-between align-items-center py-3 px-4" style={{ backgroundColor: '#07070a' }}>
                                                <div className="d-flex align-items-center gap-3">
                                                    <span className="fw-bold font-monospace fs-5 text-white">
                                                        MÃ VÉ: <span style={{ color: '#ff4d4d' }}>{ticketCode}</span>
                                                    </span>
                                                    <Badge bg="danger" className="px-3 py-1 text-uppercase fw-bold">
                                                        1 Vé xem phim
                                                    </Badge>
                                                </div>
                                                <Badge bg="success" className="px-3 py-2 fs-6 fw-bold">
                                                    ĐÃ THANH TOÁN
                                                </Badge>
                                            </Card.Header>

                                            {/* Body Thẻ Vé Layout Chuẩn Rạp */}
                                            <Card.Body className="p-4">
                                                <Row className="align-items-center">
                                                    {/* Ảnh Poster Phim */}
                                                    <Col md={3} className="text-center mb-3 mb-md-0">
                                                        <img 
                                                            src={posterUrl} 
                                                            alt={movieTitle}
                                                            className="rounded shadow border border-secondary img-fluid" 
                                                            style={{ maxHeight: '200px', objectFit: 'cover' }} 
                                                        />
                                                    </Col>

                                                    {/* Thông tin Phim & Ghế */}
                                                    <Col md={6}>
                                                        <h3 className="fw-bold text-white mb-2">{movieTitle}</h3>
                                                        <p className="text-white fw-bold mb-3 fs-6">
                                                            <span className="text-danger">📍 Chi nhánh:</span> {cinemaName} - {roomName}
                                                        </p>

                                                        <div className="p-3 rounded border border-secondary" style={{ backgroundColor: '#07070a' }}>
                                                            <div className="d-flex justify-content-between mb-2">
                                                                <span className="text-white opacity-75 fw-semibold">Suất chiếu:</span>
                                                                <span className="fs-6 fw-bold text-white">{showDate} {showTime && `| ${showTime}`}</span>
                                                            </div>
                                                            <div className="d-flex justify-content-between mb-2">
                                                                <span className="text-white opacity-75 fw-semibold">Vị trí ghế ngồi (1 vé):</span>
                                                                <span className="fs-4 fw-bold text-warning">{seatNumber}</span>
                                                            </div>
                                                            <div className="d-flex justify-content-between">
                                                                <span className="text-white opacity-75 fw-semibold">Giá vé:</span>
                                                                <span className="fs-5 fw-bold" style={{ color: '#ff4d4d' }}>{ticketPrice.toLocaleString("vi-VN")} đ</span>
                                                            </div>
                                                        </div>
                                                    </Col>

                                                    {/* Khung Mã QR Code để Soát Vé */}
                                                    <Col md={3} className="text-center mt-3 mt-md-0 border-start border-secondary ps-md-3">
                                                        <small className="text-white opacity-90 fw-bold d-block mb-2">MÃ QR SOÁT VÉ</small>
                                                        <div className="p-2 bg-white d-inline-block rounded shadow-sm border border-danger mb-2">
                                                            <img 
                                                                src={`https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${ticketCode}`} 
                                                                alt={`QR ${ticketCode}`}
                                                                width="120"
                                                                height="120"
                                                            />
                                                        </div>
                                                        <small className="text-white font-monospace d-block small">
                                                            Quét mã tại cổng rạp
                                                        </small>
                                                    </Col>
                                                </Row>
                                            </Card.Body>
                                        </Card>
                                    );
                                })
                            ) : (
                                <Card className="text-white border-danger shadow-lg overflow-hidden w-100 p-4" style={{ maxWidth: '850px', backgroundColor: '#14141d' }}>
                                    <Row className="align-items-center">
                                        <Col md={9}>
                                            <h3 className="fw-bold text-white mb-2">{movieTitle}</h3>
                                            <p className="text-white opacity-90 fs-6">Đơn đặt vé #{bookingId} đã được lưu thành công vào hệ thống.</p>
                                        </Col>
                                        <Col md={3} className="text-center">
                                            <div className="p-2 bg-white d-inline-block rounded border border-danger">
                                                <img 
                                                    src={`https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=TK-${bookingId}`} 
                                                    alt={`QR ${bookingId}`}
                                                    width="120"
                                                    height="120"
                                                />
                                            </div>
                                        </Col>
                                    </Row>
                                </Card>
                            )}
                        </div>

                        {/* Thanh nút bấm Thao Tác: In vé / Lưu vé & Xem Vé Của Tôi */}
                        <div className="text-center mt-5 d-flex justify-content-center gap-3 flex-wrap">
                            <Button variant="danger" size="lg" onClick={handlePrintTicket} className="fw-bold px-4 py-2" style={{ backgroundColor: '#dc2626', borderColor: '#dc2626' }}>
                                🖨️ In / Tải Vé Về Máy (PDF)
                            </Button>
                            <Link to="/lich-su-dat-ve" className="btn btn-outline-light size-lg px-4 py-2 fw-bold fs-5">
                                🎟️ Xem Tất Cả Vé Của Tôi
                            </Link>
                            <Link to="/" className="btn btn-outline-secondary size-lg px-4 py-2 fw-bold fs-5">
                                Trang chủ
                            </Link>
                        </div>
                    </div>
                ) : (
                    <Card className="text-white border-danger shadow-lg text-center p-4 m-auto" style={{ maxWidth: '650px', backgroundColor: '#14141d', borderLeft: '6px solid #dc2626' }}>
                        <Card.Body>
                            <div className="mb-3">
                                <span className="badge bg-danger px-4 py-2 fs-5">THANH TOÁN ĐÃ HỦY / THẤT BẠI</span>
                            </div>
                            <h3 className="fw-bold text-white mb-3">Giao dịch VNPay không thành công</h3>
                            <p className="text-white opacity-75 mb-3">
                                Quá trình thanh toán trực tuyến đã bị hủy hoặc gặp sự cố.
                            </p>
                            <p className="text-warning fw-bold mb-4 small">
                                Ghế của bạn đã được tự động giải phóng về trạng thái ban đầu để người khác hoặc bạn có thể chọn lại.
                            </p>

                            <div className="d-flex justify-content-center gap-3">
                                <Link to="/" className="btn btn-warning px-4 py-2 fw-bold text-dark">
                                    Thử lại
                                </Link>
                                <Link to="/lich-su-dat-ve" className="btn btn-outline-light px-4 py-2 fw-bold">
                                    Quay về
                                </Link>
                            </div>
                        </Card.Body>
                    </Card>
                )}
            </Container>
        </div>
    );
};

export default VNPayReturn;
