import React, { useEffect, useState, useContext } from 'react';
import { Container, Card, Badge, Button, Row, Col, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { authApis, endpoints } from '../../configs/Apis';
import { MyUserContext } from '../../configs/context';
import MySpinner from '../../components/MySpinner/MySpinner';

const Ticket = () => {
    const [user] = useContext(MyUserContext);
    const [ticketsList, setTicketsList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadMyTickets = async () => {
        if (!user) {
            setLoading(false);
            return;
        }

        setLoading(true);
        setError("");
        try {
            const res = await authApis().get(endpoints.my_bookings);
            const bookings = Array.isArray(res.data) ? res.data : (res.data?.results || []);
            
            // Sắp xếp đơn đặt vé mới nhất lên trước (giảm dần theo thời gian/ID)
            const sortedBookings = [...bookings].sort((a, b) => {
                const timeA = new Date(a.created_at || 0).getTime();
                const timeB = new Date(b.created_at || 0).getTime();
                if (timeB !== timeA) return timeB - timeA;
                return (b.id || 0) - (a.id || 0);
            });

            const paidBookings = sortedBookings.filter(b => b.payment_status === 'PAID');

            // Tách từng đơn vé (Booking) thành từng Vé cá thể (1 Vé = 1 Ghế)
            const allTickets = [];
            paidBookings.forEach((b) => {
                const movieTitle = b.movie_title || b.showtime?.movie?.movie_name || "Phim chiếu rạp";
                const posterUrl = b.movie_poster || b.showtime?.movie?.poster || "https://res.cloudinary.com/dxxwcby8l/image/upload/v1717013892/Cinemax-Placeholder-Gold-Star_d3k4e0.jpg";
                const cinemaName = b.cinema_name || b.showtime?.room?.cinema?.name || "Rạp CineBook";
                const roomName = b.room_name || b.showtime?.room?.name || "Phòng chiếu";
                const showDate = b.showtime_date || b.showtime?.show_date || "";
                const showTime = b.showtime_time || b.showtime?.start_time || "";
                const tickets = b.tickets || [];

                if (tickets.length > 0) {
                    tickets.forEach((t, idx) => {
                        const tCode = t.ticket_code || t.id || `TK-${b.id}-${idx + 1}`;
                        allTickets.push({
                            ticket_id: tCode,
                            booking_id: b.id,
                            movieTitle,
                            posterUrl,
                            cinemaName,
                            roomName,
                            showDate,
                            showTime,
                            seatNumber: t.seat_number || t.seat?.seat_number || "A1",
                            price: t.price || (b.total_price / (tickets.length || 1)) || 75000,
                            paymentMethod: b.payment_method || "CASH",
                            createdAt: b.created_at
                        });
                    });
                } else {
                    const tCode = `TK-${b.id}`;
                    allTickets.push({
                        ticket_id: tCode,
                        booking_id: b.id,
                        movieTitle,
                        posterUrl,
                        cinemaName,
                        roomName,
                        showDate,
                        showTime,
                        seatNumber: "Ghế đã chọn",
                        price: b.total_price || 75000,
                        paymentMethod: b.payment_method || "CASH",
                        createdAt: b.created_at
                    });
                }
            });

            // Tối đa chỉ lưu và hiển thị 5 vé mua thời gian gần nhất, các vé cũ hơn tự động bỏ qua
            const recentTickets = allTickets.slice(0, 5);

            setTicketsList(recentTickets);
        } catch (err) {
            console.error("Lỗi khi tải lịch sử vé:", err);
            setError("Không thể tải danh sách vé. Vui lòng kiểm tra lại kết nối.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMyTickets();
    }, [user]);

    const handlePrintAll = () => {
        window.print();
    };

    if (!user) {
        return (
            <div style={{ backgroundColor: '#0d0d12', minHeight: '100vh', paddingTop: '40px' }}>
                <Container className="text-center text-white">
                    <div className="p-5 border border-danger rounded shadow" style={{ backgroundColor: '#14141d' }}>
                        <h3 className="text-danger fw-bold">Vui lòng đăng nhập</h3>
                        <p className="text-white opacity-75">Bạn cần đăng nhập để xem danh sách vé xem phim của mình.</p>
                        <Link to="/login" className="btn btn-danger px-4 py-2 fw-bold mt-2" style={{ backgroundColor: '#dc2626', borderColor: '#dc2626' }}>
                            Đăng nhập ngay
                        </Link>
                    </div>
                </Container>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="spinner-overlay">
                <MySpinner />
            </div>
        );
    }

    return (
        <div style={{ backgroundColor: '#0d0d12', minHeight: '100vh', paddingTop: '20px', paddingBottom: '60px' }}>
            <Container className="text-white">
                <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-danger flex-wrap gap-2">
                    <div>
                        <h2 className="fw-bold text-uppercase mb-1" style={{ color: '#ff4d4d', letterSpacing: '1px' }}>
                            Vé Của Tôi (Vé Đã Đặt)
                        </h2>
                        <p className="text-white mb-0 fs-6">Mỗi vé tương ứng 1 ghế ngồi đã xuất kèm mã QR Code soát vé tại rạp</p>
                    </div>
                    <div className="d-flex gap-2">
                        <Button variant="danger" size="sm" onClick={handlePrintAll} className="fw-bold text-white px-3" style={{ backgroundColor: '#dc2626', borderColor: '#dc2626' }}>
                            🖨️ In / Tải Vé (PDF)
                        </Button>
                        <Button variant="outline-danger" size="sm" onClick={loadMyTickets} className="fw-bold text-white border-danger">
                            Tải lại
                        </Button>
                    </div>
                </div>

                {error && <Alert variant="danger">{error}</Alert>}

                {ticketsList.length === 0 ? (
                    <div className="text-center py-5 border border-danger border-dashed rounded my-4" style={{ backgroundColor: '#14141d' }}>
                        <h4 className="text-white fw-bold mb-2">Bạn chưa có vé xem phim nào</h4>
                        <p className="text-white opacity-75 mb-3">Hãy chọn bộ phim yêu thích và đặt vé xem phim ngay hôm nay!</p>
                        <Link to="/" className="btn btn-danger px-4 py-2 fw-bold" style={{ backgroundColor: '#dc2626', borderColor: '#dc2626' }}>
                            Khám phá phim ngay
                        </Link>
                    </div>
                ) : (
                    <div className="d-flex flex-column gap-4 align-items-center">
                        {ticketsList.map((ticket, idx) => (
                            <Card key={`${ticket.ticket_id}-${idx}`} className="text-white border-danger shadow-lg overflow-hidden w-100 printable-ticket" style={{ maxWidth: '850px', backgroundColor: '#14141d', borderLeft: '8px solid #dc2626' }}>
                                
                                {/* Header 1 Vé = 1 Ghế */}
                                <Card.Header className="d-flex justify-content-between align-items-center py-3 px-4 border-secondary" style={{ backgroundColor: '#07070a' }}>
                                    <div className="d-flex align-items-center gap-3">
                                        <span className="fw-bold font-monospace fs-5 text-white">
                                            MÃ VÉ: <span style={{ color: '#ff4d4d' }}>{ticket.ticket_id}</span>
                                        </span>
                                        <Badge bg="danger" className="px-3 py-1 text-uppercase fw-bold">
                                            1 Vé xem phim
                                        </Badge>
                                    </div>
                                    <Badge bg="success" className="px-3 py-2 fs-6 fw-bold">
                                        ĐÃ THANH TOÁN
                                    </Badge>
                                </Card.Header>

                                {/* Body Thẻ Vé Chuẩn Rạp Chiếu */}
                                <Card.Body className="p-4">
                                    <Row className="align-items-center">
                                        
                                        {/* Cột Trái: Ảnh Poster Phim */}
                                        <Col md={3} className="text-center mb-3 mb-md-0">
                                            <img 
                                                src={ticket.posterUrl} 
                                                alt={ticket.movieTitle}
                                                className="rounded shadow border border-secondary img-fluid" 
                                                style={{ maxHeight: '190px', objectFit: 'cover' }} 
                                            />
                                        </Col>

                                        {/* Cột Giữa: Thông tin Phim & Suất chiếu & Ghế */}
                                        <Col md={6}>
                                            <h3 className="fw-bold text-white mb-2">{ticket.movieTitle}</h3>
                                            <p className="text-white fw-bold mb-3 fs-6">
                                                <span className="text-danger">📍 Chi nhánh:</span> {ticket.cinemaName} - {ticket.roomName}
                                            </p>

                                            <div className="p-3 rounded border border-secondary" style={{ backgroundColor: '#07070a' }}>
                                                <div className="d-flex justify-content-between mb-2">
                                                    <span className="text-white opacity-75 fw-semibold">Suất chiếu:</span>
                                                    <span className="fs-6 fw-bold text-white">{ticket.showDate} {ticket.showTime && `| ${ticket.showTime}`}</span>
                                                </div>
                                                <div className="d-flex justify-content-between mb-2">
                                                    <span className="text-white opacity-75 fw-semibold">Vị trí ghế ngồi (1 vé):</span>
                                                    <span className="fs-4 fw-bold text-warning">{ticket.seatNumber}</span>
                                                </div>
                                                <div className="d-flex justify-content-between">
                                                    <span className="text-white opacity-75 fw-semibold">Giá vé:</span>
                                                    <span className="fs-5 fw-bold" style={{ color: '#ff4d4d' }}>{(ticket.price || 75000).toLocaleString("vi-VN")} đ</span>
                                                </div>
                                            </div>
                                        </Col>

                                        {/* Cột Phải: Mã QR Code để Soát Vé */}
                                        <Col md={3} className="text-center mt-3 mt-md-0 border-start border-secondary ps-md-3">
                                            <small className="text-white opacity-90 fw-bold d-block mb-2">MÃ QR SOÁT VÉ</small>
                                            <div className="p-2 bg-white d-inline-block rounded shadow-sm border border-danger mb-2">
                                                <img 
                                                    src={`https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${ticket.ticket_id}`} 
                                                    alt={`QR ${ticket.ticket_id}`}
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
                        ))}
                    </div>
                )}
            </Container>
        </div>
    );
};

export default Ticket;
