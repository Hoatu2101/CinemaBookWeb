import { useState } from "react";
import { Card, Button } from "react-bootstrap";

const ShowtimeSelector = ({ showtimes, onSelect }) => {
    const [selectedId, setSelectedId] = useState(null);

    const handleSelect = (showtime) => {
        setSelectedId(showtime.id);
        onSelect(showtime);
    };

    return (
        <div className="mt-3">
            <h5 className="text-white mb-3">Chọn suất chiếu</h5>

            <div className="d-flex flex-wrap gap-2">
                {showtimes.map(st => (
                    <Button
                        key={st.id}
                        variant={selectedId === st.id ? "warning" : "outline-light"}
                        onClick={() => handleSelect(st)}
                        style={{ minWidth: "140px" }}
                    >
                        {st.room?.name} <br />
                        {new Date(st.startTime).toLocaleTimeString()}
                    </Button>
                ))}
            </div>
        </div>
    );
};

export default ShowtimeSelector;