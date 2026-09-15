import React, { useState, useContext, useRef, useEffect } from 'react';
import { MyUserContext } from '../configs/context';
import Apis from '../configs/Apis';

const ChatWidget = () => {
    const [user] = useContext(MyUserContext);
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            sender: 'ai',
            text: 'Xin chào! Tôi là Trợ lý AI CineBook. Tôi có thể hỗ trợ bạn về lịch chiếu phim, giá vé, đặt vé online và dịch vụ của rạp phim CineBook.'
        }
    ]);
    const [inputPrompt, setInputPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);


    if (!user) {
        return null;
    }

    const handleSendMessage = async (e) => {
        e.preventDefault();
        const text = inputPrompt.trim();
        if (!text || loading) return;

        // Thêm câu hỏi của user vào danh sách
        const userMsg = { sender: 'user', text };
        setMessages((prev) => [...prev, userMsg]);
        setInputPrompt('');
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('prompt', text);

            const res = await Apis.post('/chat/', formData);
            if (res.data && res.data.status === 'success') {
                setMessages((prev) => [...prev, { sender: 'ai', text: res.data.reply }]);
            } else {
                setMessages((prev) => [...prev, { sender: 'ai', text: res.data?.message || 'Có lỗi xảy ra, vui lòng thử lại!' }]);
            }
        } catch (err) {
            console.error('Lỗi Gemini AI Chat:', err);
            setMessages((prev) => [
                ...prev,
                { sender: 'ai', text: 'Xin lỗi, không thể kết nối tới server AI lúc này. Vui lòng kiểm tra lại kết nối!' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 9999 }}>
            {/* Nút bật/tắt Chatbox - Thiết kế Đỏ/Đen hình vuông */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    style={{
                        backgroundColor: '#dc2626',
                        color: '#ffffff',
                        border: '2px solid #ff4d4d',
                        borderRadius: '0px',
                        padding: '12px 22px',
                        fontWeight: 'bold',
                        fontSize: '0.95rem',
                        letterSpacing: '0.5px',
                        boxShadow: '0 8px 24px rgba(220, 38, 38, 0.4)',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                    }}
                >
                    HỖ TRỢ AI CINEBOOK
                </button>
            )}

            {/* Khung Hộp Chatbox - Hình vuông màu Đỏ & Đen */}
            {isOpen && (
                <div
                    style={{
                        width: '360px',
                        maxWidth: '90vw',
                        height: '480px',
                        maxHeight: '80vh',
                        backgroundColor: '#14141d',
                        border: '2px solid #dc2626',
                        borderRadius: '0px',
                        boxShadow: '0 12px 32px rgba(0, 0, 0, 0.8)',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden'
                    }}
                >
                    {/* Header Của Chatbox */}
                    <div
                        style={{
                            backgroundColor: '#07070a',
                            borderBottom: '1px solid #dc2626',
                            padding: '14px 18px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}
                    >
                        <div>
                            <span style={{ color: '#ff4d4d', fontWeight: 'bold', fontSize: '1rem', letterSpacing: '0.5px' }}>
                                TRỢ LÝ AI CINEBOOK
                            </span>
                            <small style={{ display: 'block', color: '#9ca3af', fontSize: '0.75rem' }}>
                                Trả lời thông tin hệ thống rạp
                            </small>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            style={{
                                backgroundColor: '#272738',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '0px',
                                padding: '4px 12px',
                                fontSize: '0.85rem',
                                fontWeight: 'bold',
                                cursor: 'pointer'
                            }}
                        >
                            Đóng
                        </button>
                    </div>

                    {/* Nội dung tin nhắn */}
                    <div
                        style={{
                            flex: 1,
                            padding: '16px',
                            overflowY: 'auto',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '12px',
                            backgroundColor: '#0d0d12'
                        }}
                    >
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                style={{
                                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                                    maxWidth: '82%',
                                    backgroundColor: msg.sender === 'user' ? '#dc2626' : '#1e1e2d',
                                    color: '#ffffff',
                                    padding: '10px 14px',
                                    borderRadius: msg.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                                    fontSize: '0.9rem',
                                    lineHeight: '1.45',
                                    border: msg.sender === 'user' ? 'none' : '1px solid #3f3f5a',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                                    whiteSpace: 'pre-line'
                                }}
                            >
                                {msg.text}
                            </div>
                        ))}
                        {loading && (
                            <div
                                style={{
                                    alignSelf: 'flex-start',
                                    backgroundColor: '#1e1e2d',
                                    color: '#ff4d4d',
                                    padding: '8px 14px',
                                    borderRadius: '12px',
                                    fontSize: '0.85rem',
                                    fontStyle: 'italic',
                                    border: '1px solid #3f3f5a'
                                }}
                            >
                                AI đang tìm câu trả lời...
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>

                    {/* Thanh nhập liệu và gửi tin nhắn */}
                    <form
                        onSubmit={handleSendMessage}
                        style={{
                            padding: '12px',
                            backgroundColor: '#07070a',
                            borderTop: '1px solid #272738',
                            display: 'flex',
                            gap: '8px'
                        }}
                    >
                        <input
                            type="text"
                            value={inputPrompt}
                            onChange={(e) => setInputPrompt(e.target.value)}
                            placeholder="Hỏi lịch chiếu, giá vé, đặt vé..."
                            disabled={loading}
                            style={{
                                flex: 1,
                                backgroundColor: '#14141d',
                                border: '1px solid #3f3f5a',
                                borderRadius: '0px',
                                padding: '8px 12px',
                                color: '#ffffff',
                                fontSize: '0.9rem',
                                outline: 'none'
                            }}
                        />
                        <button
                            type="submit"
                            disabled={loading || !inputPrompt.trim()}
                            style={{
                                backgroundColor: '#dc2626',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '0px',
                                padding: '8px 16px',
                                fontWeight: 'bold',
                                fontSize: '0.9rem',
                                cursor: loading || !inputPrompt.trim() ? 'not-allowed' : 'pointer',
                                opacity: loading || !inputPrompt.trim() ? 0.5 : 1
                            }}
                        >
                            Gửi
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default ChatWidget;
