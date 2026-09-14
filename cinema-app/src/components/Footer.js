import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Footer.css'; 

const Footer = () => {
    return (
        <footer className="cinema-footer">
            <div className="footer-container">
               
                <div className="footer-col brand-col">
                    <h2 className="footer-brand"><span className="text-red">CINE</span>BOOK</h2>
                    <p className="footer-desc">
                        Hệ thống đặt vé xem phim trực tuyến hàng đầu. Mang đến trải nghiệm điện ảnh đỉnh cao, đặt vé nhanh chóng và tiện lợi nhất.
                    </p>
                </div>

               
                <div className="footer-col">
                    <h3 className="footer-title">Khám Phá</h3>
                    <div className="footer-links">
                        <Link to="/phim" className="footer-link">Phim Đang Chiếu</Link>
                        <Link to="/phim" className="footer-link">Phim Sắp Chiếu</Link>
                        <Link to="/lich-su-dat-ve" className="footer-link">Vé Của Tôi</Link>
                    </div>
                </div>

            
                <div className="footer-col">
                    <h3 className="footer-title">Hỗ Trợ</h3>
                    <div className="footer-links">
                        <a href="#" className="footer-link">Điều khoản sử dụng</a>
                        <a href="#" className="footer-link">Chính sách bảo mật</a>
                        <a href="#" className="footer-link">Liên hệ & Góp ý</a>
                    </div>
                </div>
            </div>

          
            <div className="footer-bottom">
                <p>Copyright © 2026 CineBook. All rights reserved.</p>
            </div>
        </footer>
    );
}

export default Footer;