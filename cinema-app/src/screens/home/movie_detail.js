import '../../styles/movie.css';
import { useEffect, useState, useRef, lazy, Suspense } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import Apis, { endpoints } from '../../configs/Apis';
import MySpinner from '../../components/MySpinner/MySpinner';

// Lazy load các component con khi thực sự cần thiết
const ShowtimeList = lazy(() => import('./showtimelist'));
const SeatMap = lazy(() => import('./SeatMap'));

const MovieDetails = () => {
    const { movieId } = useParams();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);

    const [selectedShowtime, setSelectedShowtime] = useState(null);
    const seatMapRef = useRef(null);

    const loadProduct = async () => {
        setLoading(true);
        try {
            if (movieId) {
                let res = await Apis.get(
                    endpoints['detail_movie'](movieId)
                );
                setMovie(res.data);
            }
        } catch (ex) {
            console.error("Lỗi:", ex);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadProduct();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [movieId]);

    const handleSelectShowtime = (showtimeId) => {
        setSelectedShowtime(showtimeId);
        setTimeout(() => {
            if (seatMapRef.current) {
                seatMapRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    };

    if (loading) return <div className="spinner-overlay"><MySpinner /></div>;
    if (!movie) return <h3 className="text-white text-center mt-5">Không tìm thấy thông tin phim!</h3>;

    const categoryName = Array.isArray(movie.categories) && movie.categories.length > 0
        ? movie.categories.map(c => c.name).join(", ")
        : (movie.category?.name || "Phim chiếu rạp");

    return (
        <div className="movie-details-wrapper">
            <div
                className="hero-banner"
                style={{ backgroundImage: `url(${movie.poster || "https://res.cloudinary.com/dxxwcby8l/image/upload/v1717013892/Cinemax-Placeholder-Gold-Star_d3k4e0.jpg"})` }}
            >
                <div className="hero-overlay">
                    <Container className="hero-content">
                        <div className="category-tags">
                            <span className="custom-tag">
                                {categoryName}
                            </span>
                        </div>
                        <h1 className="hero-title">{movie.movie_name || movie.movieName || "Chi tiết phim"}</h1>

                        <div className="meta-info">
                            <span className="meta-item text-warning">
                                <b>⭐ {movie.rating || "8.9"}/10</b>
                            </span>
                            <span className="meta-item"> Thời lượng: {movie.duration || 120} phút</span>
                            {movie.actor && <span className="meta-item"> Diễn viên: {movie.actor}</span>}
                            {movie.drirector && <span className="meta-item"> Đạo diễn: {movie.drirector}</span>}
                        </div>
                    </Container>
                </div>
            </div>

            <Container className="content-section mt-4">
                <Row>
                    <Col md={7} lg={8} className="mb-4">
                        <h4 className="section-heading">Nội dung phim</h4>
                        <p className="movie-description">{movie.description || "Chưa có mô tả nội dung cho bộ phim này."}</p>
                    </Col>
                </Row>


                <Row className="mt-5">
                    <Col>
                        <Suspense fallback={<MySpinner />}>
                            <ShowtimeList movieId={movieId} onSelectShowtime={handleSelectShowtime} />
                        </Suspense>
                    </Col>
                </Row>


                <hr style={{ borderColor: '#4b4b8f', margin: '40px 0' }} />

                <div ref={seatMapRef}>
                    {selectedShowtime ? (
                        <Row className="mb-5 pb-5">
                            <Col>
                                <Suspense fallback={<MySpinner />}>
                                    <SeatMap showtimeId={selectedShowtime} />
                                </Suspense>
                            </Col>
                        </Row>
                    ) : (
                        <div className="text-center py-5 mb-5" style={{ color: '#6a6a9d' }}>
                            <i className="fs-1">!</i>
                            <p className="mt-3">Sơ đồ ghế sẽ xuất hiện ở đây sau khi bạn chọn suất chiếu.</p>
                        </div>
                    )}
                </div>

            </Container>
        </div>
    );
};

export default MovieDetails;