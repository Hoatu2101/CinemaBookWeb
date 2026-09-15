import React from 'react';
import { Modal, Button } from 'react-bootstrap';

/**
 * Component Popup thông báo tùy chỉnh thay thế cho alert() mặc định của trình duyệt
 */
const NotificationModal = ({ show, onHide, title, message, variant = 'danger', confirmText = 'Đã hiểu' }) => {
    const getIcon = () => {
        switch (variant) {
            case 'success':
                return '✅';
            case 'warning':
                return '⚠️';
            case 'info':
                return 'ℹ️';
            case 'danger':
            default:
                return '🔔';
        }
    };

    const getThemeColor = () => {
        switch (variant) {
            case 'success':
                return '#16a34a';
            case 'warning':
                return '#d97706';
            case 'info':
                return '#2563eb';
            case 'danger':
            default:
                return '#e50914';
        }
    };

    const themeColor = getThemeColor();

    return (
        <Modal 
            show={show} 
            onHide={onHide} 
            centered 
            backdrop="static"
            keyboard={true}
        >
            <div style={{
                backgroundColor: '#14141d',
                color: '#ffffff',
                borderRadius: '12px',
                border: `1px solid ${themeColor}`,
                overflow: 'hidden',
                boxShadow: '0 10px 30px rgba(0,0,0,0.7)'
            }}>
                <div style={{
                    backgroundColor: themeColor,
                    padding: '14px 20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '20px' }}>{getIcon()}</span>
                        <h5 className="mb-0 fw-bold text-white text-uppercase" style={{ letterSpacing: '0.5px' }}>
                            {title || 'Thông báo CineBook'}
                        </h5>
                    </div>
                    <button 
                        type="button" 
                        className="btn-close btn-close-white" 
                        onClick={onHide}
                        aria-label="Close"
                    ></button>
                </div>

                <div style={{ padding: '24px 20px', fontSize: '15px', lineHeight: '1.6', color: '#f1f5f9' }}>
                    {message}
                </div>

                <div style={{
                    padding: '12px 20px 20px',
                    display: 'flex',
                    justifyContent: 'flex-end'
                }}>
                    <Button 
                        onClick={onHide}
                        style={{
                            backgroundColor: themeColor,
                            borderColor: themeColor,
                            color: '#ffffff',
                            fontWeight: '600',
                            padding: '8px 24px',
                            borderRadius: '6px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        {confirmText}
                    </Button>
                </div>
            </div>
        </Modal>
    );
};

export default NotificationModal;
