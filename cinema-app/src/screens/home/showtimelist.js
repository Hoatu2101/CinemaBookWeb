import { useEffect, useState } from "react";
import Apis, { endpoints } from "../../configs/Apis";
import "../../styles/movie.css";

const getLocalDateStr = (d = new Date()) => {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const isShowtimePast = (st) => {
    if (!st || !st.show_date) return false;
    const now = new Date();
    const [y, m, d] = st.show_date.split('-').map(Number);
    let hour = 0, minute = 0;
    const timeStr = st.start_time || st.startTime;
    if (timeStr && typeof timeStr === "string" && timeStr.includes(":")) {
        const parts = timeStr.split(":").map(Number);
        hour = parts[0] || 0;
        minute = parts[1] || 0;
    } else if (timeStr) {
        const dateObj = new Date(timeStr);
        if (!isNaN(dateObj.getTime())) {
            hour = dateObj.getHours();
            minute = dateObj.getMinutes();
        }
    }
    const showtimeDate = new Date(y, m - 1, d, hour, minute, 0);
    return showtimeDate < now;
};

const ShowtimeList = ({ movieId, onSelectShowtime }) => {
    const todayStr = getLocalDateStr();
    const [showtimes, setShowtimes] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [selectedDate, setSelectedDate] = useState(todayStr);
    const [hidePast, setHidePast] = useState(true);

    const getUpcomingDays = (count = 7) => {
        const days = [];
        const today = new Date();
        for (let i = 0; i < count; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            const iso = getLocalDateStr(d);
            let label = "";
            if (i === 0) label = "Hôm nay";
            else if (i === 1) label = "Ngày mai";
            else {
                const dayNames = ["Chủ Nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
                label = `${dayNames[d.getDay()]} ${d.getDate()}/${d.getMonth() + 1}`;
            }
            days.push({ iso, label });
        }
        return days;
    };

    const upcomingDays = getUpcomingDays(7);

    useEffect(() => {
        const loadShowtimes = async () => {
            try {
                const res = await Apis.get(endpoints.movie_showtimes(movieId));
                const list = Array.isArray(res.data) ? res.data : (res.data?.results || []);
                setShowtimes(list);

                // Nếu có suất chiếu, mặc định chọn ngày của suất chiếu sớm nhất (nếu không phải hôm nay)
                if (list.length > 0 && list[0].show_date) {
                    const validDates = list.map(s => s.show_date).filter(d => d >= todayStr);
                    if (validDates.length > 0 && !validDates.includes(todayStr)) {
                        setSelectedDate(validDates[0]);
                    }
                }
            } catch (err) {
                console.error("Lỗi khi tải lịch chiếu:", err);
                setShowtimes([]);
            }
        };

        if (movieId) loadShowtimes();
    }, [movieId, todayStr]);

    const formatTime = (time) => {
        if (!time) return "--:--";
        if (typeof time === "string" && time.includes(":")) {
            const parts = time.split(":");
            return `${parts[0]}:${parts[1]}`;
        }
        const date = new Date(time);
        if (!isNaN(date.getTime())) {
            return date.toLocaleTimeString("vi-VN", {
                hour: "2-digit",
                minute: "2-digit",
            });
        }
        return time;
    };

    // Lọc các suất chiếu theo Ngày đã chọn (và công tắc Ẩn suất chiếu đã qua)
    const showtimesForDate = showtimes.filter((st) => {
        if (!st.show_date) return true;
        if (st.show_date !== selectedDate) return false;
        if (hidePast && isShowtimePast(st)) return false;
        return true;
    });

    const groupByCinema = (data) => {
        if (!Array.isArray(data)) return {};
        
        return data.reduce((groups, st) => {
            const baseName = st.cinema_name || st.cinemaName || st.room?.cinema?.name || "Rạp CineBook";
            const location = st.cinema_location || st.cinemaLocation || st.room?.cinema?.location;
            const fullCinemaName = location ? `${baseName} (${location})` : baseName;

            if (!groups[fullCinemaName]) {
                groups[fullCinemaName] = [];
            }
            groups[fullCinemaName].push(st);
            return groups;
        }, {});
    };

    const handleSelect = (st) => {
        if (isShowtimePast(st)) {
            alert("Suất chiếu này đã qua thời gian khởi chiếu!");
            return;
        }
        setSelectedId(st.id);
        if (onSelectShowtime) {
            onSelectShowtime(st); 
        }
    };

    const handleDateChange = (dateVal) => {
        if (dateVal < todayStr) {
            alert("Không thể chọn ngày trong quá khứ!");
            return;
        }
        setSelectedDate(dateVal);
        setSelectedId(null);
    };

    const groupedShowtimes = groupByCinema(showtimesForDate);
    const cinemaList = Object.keys(groupedShowtimes);

    return (
        <div className="showtime-container my-4 p-4 rounded shadow bg-dark border border-secondary text-white">
            
            {/* Header */}
            <div className="mb-4">
                <h4 className="section-heading mb-0 fw-bold text-uppercase text-warning">
                    Lịch Chiếu Phim
                </h4>
            </div>

            {/* BỘ CHỌN NGÀY CHIẾU (Không cho chọn ngày quá khứ) */}
            <div className="mb-4 p-3 rounded bg-black bg-opacity-50 border border-secondary">
                <div className="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
                    <div className="d-flex align-items-center gap-2">
                        <span className="fw-bold text-info">Chọn ngày chiếu:</span>
                        <input
                            type="date"
                            min={todayStr}
                            value={selectedDate}
                            onChange={(e) => handleDateChange(e.target.value)}
                            className="form-control bg-dark text-white border-secondary"
                            style={{ maxWidth: "180px" }}
                        />
                    </div>

                    <div className="form-check form-switch text-light my-1">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            role="switch"
                            id="hidePastSwitch"
                            checked={hidePast}
                            onChange={(e) => setHidePast(e.target.checked)}
                            style={{ cursor: "pointer" }}
                        />
                        <label className="form-check-label text-secondary small fw-semibold ms-1" htmlFor="hidePastSwitch" style={{ cursor: "pointer" }}>
                            Ẩn suất chiếu đã qua
                        </label>
                    </div>
                </div>

                <div className="d-flex gap-2 overflow-auto py-2">
                    {upcomingDays.map((day) => (
                        <button
                            key={day.iso}
                            type="button"
                            onClick={() => handleDateChange(day.iso)}
                            className={`btn text-nowrap px-3 py-2 fw-semibold ${
                                selectedDate === day.iso
                                    ? "btn-warning text-dark shadow"
                                    : "btn-outline-secondary text-light"
                            }`}
                        >
                            {day.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* DANH SÁCH TẤT CẢ CÁC RẠP CHIẾU & SUẤT CHIẾU TRỰC TIẾP */}
            {cinemaList.length > 0 ? (
                cinemaList.map((cinemaName) => (
                    <div key={cinemaName} className="cinema-group mb-4 p-3 rounded border border-secondary" style={{ backgroundColor: "#151521" }}>
                        <div className="cinema-name mb-3 d-flex align-items-center justify-content-between">
                            <span className="fs-5 fw-bold text-info">{cinemaName}</span>
                            <span className="badge bg-secondary">{groupedShowtimes[cinemaName].length} suất chiếu</span>
                        </div>
                        
                        <div className="d-flex flex-wrap gap-2">
                            {groupedShowtimes[cinemaName].map((st) => {
                                const isPast = isShowtimePast(st);
                                return (
                                    <button
                                        key={st.id}
                                        type="button"
                                        disabled={isPast}
                                        onClick={() => !isPast && handleSelect(st)}
                                        className={`btn px-3 py-2 fw-semibold ${
                                            isPast
                                                ? "btn-secondary text-muted opacity-50 border-secondary"
                                                : selectedId === st.id
                                                ? "btn-warning text-dark shadow"
                                                : "btn-outline-warning"
                                        }`}
                                        style={isPast ? { cursor: "not-allowed", textDecoration: "line-through" } : {}}
                                    >
                                        {st.room_name ? `${st.room_name} | ` : ""}
                                        {formatTime(st.start_time || st.startTime)}
                                        {isPast && <span className="ms-1 badge bg-dark text-danger fw-normal" style={{ textDecoration: "none" }}>(Đã chiếu)</span>}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ))
            ) : (
                <div className="alert alert-dark text-center py-4 border border-secondary text-muted rounded my-3" role="alert">
                    <span>Chưa có suất chiếu khả dụng cho ngày <b>{selectedDate}</b>{hidePast ? " (hoặc các suất chiếu trong ngày đã trôi qua)" : ""}. Vui lòng chọn ngày khác!</span>
                </div>
            )}
        </div>
    );
};

export default ShowtimeList;