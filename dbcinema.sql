CREATE DATABASE  IF NOT EXISTS `dbcenima` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `dbcenima`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dbcenima
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `total_price` float NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `showtime_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_booking_showtime` (`showtime_id`),
  KEY `idx_booking_user` (`user_id`),
  CONSTRAINT `fk_booking_showtime` FOREIGN KEY (`showtime_id`) REFERENCES `showtimes` (`id`),
  CONSTRAINT `fk_booking_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,120000,'2026-06-01 08:53:13',3,2),(2,120000,'2026-06-01 08:53:13',3,2),(3,95000,'2026-06-01 08:53:13',2,3),(4,90000,'2026-06-01 08:53:13',5,5),(5,90000,'2026-06-01 08:53:13',5,5);
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Action','Action movies','2026-05-29 13:15:51'),(2,'Comedy','Comedy movies','2026-05-29 13:15:51'),(3,'Horror','Horror movies','2026-05-29 13:15:51'),(4,'Animation','Animation movies','2026-05-29 13:15:51');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cinemas`
--

DROP TABLE IF EXISTS `cinemas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cinemas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cinemas`
--

LOCK TABLES `cinemas` WRITE;
/*!40000 ALTER TABLE `cinemas` DISABLE KEYS */;
INSERT INTO `cinemas` VALUES (1,'CGV Vincom','Ho Chi Minh City','2026-05-29 13:15:51'),(2,'Lotte Cinema','Ha Noi','2026-05-29 13:15:51');
/*!40000 ALTER TABLE `cinemas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `movie_name` varchar(255) NOT NULL,
  `description` text,
  `trailer` varchar(500) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `movie_format` varchar(100) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `poster` varchar(500) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `category_id` int DEFAULT NULL,
  `status_movie_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_movie_category` (`category_id`),
  KEY `fk_movie_status` (`status_movie_id`),
  KEY `idx_movie_name` (`movie_name`),
  CONSTRAINT `fk_movie_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_movie_status` FOREIGN KEY (`status_movie_id`) REFERENCES `status_movie` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES (1,'Lật Mặt 7: Một Điều Ước 2','Bộ phim tâm lý gia đình cảm động của đạo diễn Lý Hải.','https://youtube.com/watch?v=latmat7',95000,'2D',138,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780552654/md08yqmefq6oz8zwmxn9.jpg',1,NULL,2,NULL),(2,'Captain America: Brave New World','Bom tấn hành động Hollywood thế hệ mới.','https://youtube.com/watch?v=cap4',120000,'2D',125,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780552643/qdvwmbthkxexxszhisog.jpg',1,NULL,1,NULL),(3,'Con Cám','Dự án kinh dị lấy cảm hứng từ truyện cổ tích Tấm Cám.','https://youtube.com/watch?v=concam',90000,'2D',110,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550365/n7gybvttvs41qcfgonkg.jpg',1,NULL,3,NULL),(4,'Doraemon: Bản Giao Hưởng Địa Cầu','Phim hoạt hình dành cho gia đình và trẻ em mùa hè.','https://youtube.com/watch?v=dora2024',85000,'2D',115,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550313/ruhex2ck7viwhzrqs2wn.jpg',1,NULL,4,NULL),(9,'Deadpool & Wolverine','Trận chiến đa vũ trụ siêu lầy lội và bùng nổ của cặp đôi hoàn cảnh.','https://youtube.com/watch?v=deadpool3',110000,'2D',127,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550281/wqk3ybebxdywm9cfjkt7.jpg',1,NULL,1,NULL),(10,'John Wick: Chapter 4','Sát thủ huyền thoại John Wick tìm cách đánh bại Hội Đồng Tối Cao.','https://youtube.com/watch?v=johnwick4',95000,'2D',169,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550267/ygctvc1pkisgty9j0rhk.jpg',1,NULL,1,NULL),(11,'Fast X','Gia đình Dominic Toretto đối đầu với kẻ thù nguy hiểm nhất từ trước đến nay.','https://youtube.com/watch?v=fastx',100000,'3D',141,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550247/z87bg4n6rmc9pyylwryz.jpg',1,NULL,1,NULL),(12,'Furiosa: A Mad Max Saga','Hành trình sinh tồn và báo thù của nữ chiến binh Furiosa thời trẻ.','https://youtube.com/watch?v=furiosa',115000,'2D',148,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550218/ivd7r5mwgnlqktu3uzge.jpg',1,NULL,1,NULL),(13,'Gladiator II','Hậu bản của thiên sử thi mãnh liệt về đấu trường La Mã cổ đại.','https://youtube.com/watch?v=gladiator2',120000,'2D',150,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550206/likyt1hxligarm7ztt1g.jpg',1,NULL,1,NULL),(14,'Bad Boys: Ride or Die','Hai chàng cảnh sát sành điệu của Miami trở lại với phi vụ nghẹt thở.','https://youtube.com/watch?v=badboys4',95000,'2D',115,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550191/bhosgsp2dgjnh23obgx1.jpg',1,NULL,1,NULL),(16,'Mai','Câu chuyện tình yêu đầy biến cố và chiều sâu tâm lý xã hội của Mai và Dương.','https://youtube.com/watch?v=mai',90000,'2D',131,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550175/svtzpxvodksyhcqflafu.jpg',1,NULL,2,NULL),(17,'Nhà Bà Nữ','Bộ phim tâm lý gia đình xoay quanh những mâu thuẫn thế hệ đầy kịch tính.','https://youtube.com/watch?v=nhabanu',85000,'2D',102,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550158/tri3lfsgyl6f7gt0ozby.jpg',1,NULL,2,NULL),(18,'Tiệc Trăng Máu','Buổi họp mặt của nhóm bạn thân biến thành thảm họa khi chiếc điện thoại bị bóc trần.','https://youtube.com/watch?v=tiectrangmau',85000,'2D',118,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550145/fya08vjknlkfcmb7onde.jpg',1,NULL,2,NULL),(19,'Gặp Lại Chị Bầu','Hành trình thanh xuân ngọt ngào, xuyên không đầy hài hước và cảm động.','https://youtube.com/watch?v=gaplaichibau',90000,'2D',110,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550131/w15q5a5rxiqt0uarsmy2.jpg',1,NULL,2,NULL),(20,'Cô Dâu Hào Môn','Một kế hoạch phông bạt tinh vi để bước chân vào thế giới thượng lưu.','https://youtube.com/watch?v=codauhaomon',95000,'2D',114,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550112/muvovnktecmcwqfz1xq2.jpg',1,NULL,2,NULL),(21,'Siêu Lừa Gặp Siêu Lầy','Trận chiến đấu trí đầy tiếng cười giữa những kẻ lừa đảo chuyên nghiệp.','https://youtube.com/watch?v=sieulua',85000,'2D',112,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550095/jlhlfiu0qym2epkrzqbk.jpg',1,NULL,2,NULL),(22,'Exhuma: Quật Mộ Trùng Ma','Hành trình khai quật ngôi mộ bí ẩn gây rúng động phòng vé châu Á.','https://youtube.com/watch?v=exhuma',100000,'2D',134,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550075/mxeldycdsz7zh00npngq.jpg',1,NULL,3,NULL),(23,'The Conjuring: Last Rites','Phần cuối cùng trong chuỗi hành trình trừ tà cốt lõi của nhà Warren.','https://youtube.com/watch?v=conjuring4',120000,'2D',120,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550061/mel0ifsnubdqw23awczc.jpg',1,NULL,3,NULL),(24,'Kẻ Ăn Hồn','Câu chuyện kinh dị cổ trang dựa trên loạt tiểu thuyết Tết Ở Làng Địa Ngục.','https://youtube.com/watch?v=keanhon',90000,'2D',109,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550040/ihrdwktgaokr837tp5mb.jpg',1,NULL,3,NULL),(25,'A Quiet Place: Day One','Quay ngược thời gian về ngày đầu tiên quái vật thính giác đổ bộ Trái Đất.','https://youtube.com/watch?v=aquietplace4',105000,'2D',100,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550026/zmtkjiymnheofoita18t.jpg',1,NULL,3,NULL),(26,'Smile 2','Nụ cười nguyền rủa đáng sợ tiếp tục bám lấy một ngôi sao nhạc Pop nổi tiếng.','https://youtube.com/watch?v=smile2',95000,'2D',127,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780550011/f7cjjogecgvovd8hfavx.jpg',1,NULL,3,NULL),(27,'Insidious: The Red Door','Gia đình Lambert đối mặt với những con quỷ dữ trong quá khứ ở cõi Vô Định.','https://youtube.com/watch?v=insidious5',95000,'2D',107,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780549991/l3rwupnlwku9miphn5o0.jpg',1,NULL,3,NULL),(28,'Inside Out 2','Những cảm xúc mới xuất hiện khi cô bé Riley chính thức bước vào tuổi dậy thì.','https://youtube.com/watch?v=insideout2',110000,'3D',96,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780549969/u6kx4jskqub4arutxenn.jpg',1,NULL,4,NULL),(29,'Kung Fu Panda 4','Po tìm kiếm người kế vị ngôi vị Thần Long Đại Hiệp và đối đầu Tắc Kè Bông.','https://youtube.com/watch?v=kungfupanda4',90000,'2D',94,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780549955/gjyw3nicrvaoif7h2cuc.jpg',1,NULL,4,NULL),(30,'Despicable Me 44','Gru và gia đình chào đón thành viên mới cùng những rắc rối siêu quậy từ Minions.','https://youtube.com/watch?v=dm4',95000,'2D',95,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780549933/ocj5i50kzbbm3sgo8u2q.jpg',1,NULL,4,NULL),(31,'How to Train Your Dragon: The Hidden World','Hành trình tìm kiếm vùng đất bí mật của Nấc Cụt và chú rồng Răng Sún.','https://youtube.com/watch?v=httyd3',80000,'3D',104,'https://res.cloudinary.com/dxxwcby8l/image/upload/v1780549914/cpzyheqbht4uicqf2xnt.jpg',1,NULL,4,NULL);
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `capacity` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `cinema_id` int NOT NULL,
  `status_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_room_cinema` (`cinema_id`),
  KEY `fk_room_status` (`status_id`),
  CONSTRAINT `fk_room_cinema` FOREIGN KEY (`cinema_id`) REFERENCES `cinemas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_room_status` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,'Phòng Chiếu 01 (IMAX)',120,'2026-05-29 13:18:49',1,1),(2,'Phòng Chiếu 02 (2D)ff',90,'2026-05-29 13:18:49',2,1),(3,'Phòng Chiếu 03 (Gold Class)fff',40,'2026-05-29 13:18:49',2,1),(4,'Cinema Room A',100,'2026-05-29 13:18:49',2,2),(5,'Phòng chiếu B01',100,'2026-05-29 13:18:49',2,1),(7,'nguyen dat 123',20,'2026-06-02 17:52:00',2,1),(8,'Phòng chiếu IMAX',11,'2026-06-02 18:10:23',2,3),(9,'Phong chiếu VIP01',22,'2026-06-02 18:50:07',2,3),(10,'Phòng chiếu B101',22,'2026-06-02 18:51:05',2,3);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seat_showtime_status`
--

DROP TABLE IF EXISTS `seat_showtime_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seat_showtime_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `showtime_id` int NOT NULL,
  `seat_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `lock_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `showtime_id` (`showtime_id`,`seat_id`),
  UNIQUE KEY `uk_showtime_seat` (`showtime_id`,`seat_id`),
  KEY `fk_sss_seat` (`seat_id`),
  KEY `fk_sss_user` (`user_id`),
  CONSTRAINT `fk_sss_seat` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sss_showtime` FOREIGN KEY (`showtime_id`) REFERENCES `showtimes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sss_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seat_showtime_status`
--

LOCK TABLES `seat_showtime_status` WRITE;
/*!40000 ALTER TABLE `seat_showtime_status` DISABLE KEYS */;
INSERT INTO `seat_showtime_status` VALUES (1,1,4853,NULL,'AVAILABLE',NULL),(2,10,4810,NULL,'AVAILABLE',NULL),(3,1,4813,NULL,'AVAILABLE',NULL),(4,2,4834,NULL,'AVAILABLE',NULL),(5,2,4804,NULL,'AVAILABLE',NULL),(6,1,4831,NULL,'AVAILABLE',NULL),(7,1,4854,NULL,'AVAILABLE',NULL);
/*!40000 ALTER TABLE `seat_showtime_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seats`
--

DROP TABLE IF EXISTS `seats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `seat_number` varchar(10) NOT NULL,
  `is_available` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `room_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_seat_room` (`room_id`),
  CONSTRAINT `fk_seat_room` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5225 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seats`
--

LOCK TABLES `seats` WRITE;
/*!40000 ALTER TABLE `seats` DISABLE KEYS */;
INSERT INTO `seats` VALUES (1,'A01',1,'2026-05-29 13:18:49',1),(2,'A02',1,'2026-05-29 13:18:49',1),(3,'B05',1,'2026-05-29 13:18:49',1),(4,'B06',0,'2026-05-29 13:18:49',1),(5,'Vip01',1,'2026-05-29 13:18:49',1),(6,'A01',1,'2026-05-29 13:18:49',4),(7,'A02',1,'2026-05-29 13:18:49',4),(4798,'A1',1,'2026-06-02 18:54:27',2),(4799,'A2',1,'2026-06-02 18:54:27',2),(4800,'A3',1,'2026-06-02 18:54:27',2),(4801,'A4',1,'2026-06-02 18:54:27',2),(4802,'A5',1,'2026-06-02 18:54:27',2),(4803,'A6',1,'2026-06-02 18:54:27',2),(4804,'A7',1,'2026-06-02 18:54:27',2),(4805,'A8',1,'2026-06-02 18:54:27',2),(4806,'A9',1,'2026-06-02 18:54:27',2),(4807,'A10',1,'2026-06-02 18:54:27',2),(4808,'B1',1,'2026-06-02 18:54:27',2),(4809,'B2',1,'2026-06-02 18:54:27',2),(4810,'B3',1,'2026-06-02 18:54:27',2),(4811,'B4',1,'2026-06-02 18:54:27',2),(4812,'B5',1,'2026-06-02 18:54:27',2),(4813,'B6',1,'2026-06-02 18:54:27',2),(4814,'B7',1,'2026-06-02 18:54:27',2),(4815,'B8',1,'2026-06-02 18:54:27',2),(4816,'B9',1,'2026-06-02 18:54:27',2),(4817,'B10',1,'2026-06-02 18:54:27',2),(4818,'C1',1,'2026-06-02 18:54:27',2),(4819,'C2',1,'2026-06-02 18:54:27',2),(4820,'C3',1,'2026-06-02 18:54:27',2),(4821,'C4',1,'2026-06-02 18:54:27',2),(4822,'C5',1,'2026-06-02 18:54:27',2),(4823,'C6',1,'2026-06-02 18:54:27',2),(4824,'C7',1,'2026-06-02 18:54:27',2),(4825,'C8',1,'2026-06-02 18:54:27',2),(4826,'C9',1,'2026-06-02 18:54:27',2),(4827,'C10',1,'2026-06-02 18:54:27',2),(4828,'D1',1,'2026-06-02 18:54:27',2),(4829,'D2',1,'2026-06-02 18:54:27',2),(4830,'D3',1,'2026-06-02 18:54:27',2),(4831,'D4',1,'2026-06-02 18:54:27',2),(4832,'D5',1,'2026-06-02 18:54:27',2),(4833,'D6',1,'2026-06-02 18:54:27',2),(4834,'D7',1,'2026-06-02 18:54:27',2),(4835,'D8',1,'2026-06-02 18:54:27',2),(4836,'D9',1,'2026-06-02 18:54:27',2),(4837,'D10',1,'2026-06-02 18:54:27',2),(4838,'E1',1,'2026-06-02 18:54:27',2),(4839,'E2',1,'2026-06-02 18:54:27',2),(4840,'E3',1,'2026-06-02 18:54:27',2),(4841,'E4',1,'2026-06-02 18:54:27',2),(4842,'E5',1,'2026-06-02 18:54:27',2),(4843,'E6',1,'2026-06-02 18:54:27',2),(4844,'E7',1,'2026-06-02 18:54:27',2),(4845,'E8',1,'2026-06-02 18:54:27',2),(4846,'E9',1,'2026-06-02 18:54:27',2),(4847,'E10',1,'2026-06-02 18:54:27',2),(4848,'F1',1,'2026-06-02 18:54:27',2),(4849,'F2',1,'2026-06-02 18:54:27',2),(4850,'F3',1,'2026-06-02 18:54:27',2),(4851,'F4',1,'2026-06-02 18:54:27',2),(4852,'F5',1,'2026-06-02 18:54:27',2),(4853,'F6',1,'2026-06-02 18:54:27',2),(4854,'F7',1,'2026-06-02 18:54:27',2),(4855,'F8',1,'2026-06-02 18:54:27',2),(4856,'F9',1,'2026-06-02 18:54:27',2),(4857,'F10',1,'2026-06-02 18:54:27',2),(4858,'G1',1,'2026-06-02 18:54:27',2),(4859,'G2',1,'2026-06-02 18:54:27',2),(4860,'G3',1,'2026-06-02 18:54:27',2),(4861,'G4',1,'2026-06-02 18:54:27',2),(4862,'G5',1,'2026-06-02 18:54:27',2),(4863,'G6',1,'2026-06-02 18:54:27',2),(4864,'G7',1,'2026-06-02 18:54:27',2),(4865,'G8',1,'2026-06-02 18:54:27',2),(4866,'G9',1,'2026-06-02 18:54:27',2),(4867,'G10',1,'2026-06-02 18:54:27',2),(4868,'H1',1,'2026-06-02 18:54:27',2),(4869,'H2',1,'2026-06-02 18:54:27',2),(4870,'H3',1,'2026-06-02 18:54:27',2),(4871,'H4',1,'2026-06-02 18:54:27',2),(4872,'H5',1,'2026-06-02 18:54:27',2),(4873,'H6',1,'2026-06-02 18:54:27',2),(4874,'H7',1,'2026-06-02 18:54:27',2),(4875,'H8',1,'2026-06-02 18:54:27',2),(4876,'H9',1,'2026-06-02 18:54:27',2),(4877,'H10',1,'2026-06-02 18:54:27',2),(4878,'I1',1,'2026-06-02 18:54:27',2),(4879,'I2',1,'2026-06-02 18:54:27',2),(4880,'I3',1,'2026-06-02 18:54:27',2),(4881,'I4',1,'2026-06-02 18:54:27',2),(4882,'I5',1,'2026-06-02 18:54:27',2),(4883,'I6',1,'2026-06-02 18:54:27',2),(4884,'I7',1,'2026-06-02 18:54:27',2),(4885,'I8',1,'2026-06-02 18:54:27',2),(4886,'I9',1,'2026-06-02 18:54:27',2),(4887,'I10',1,'2026-06-02 18:54:27',2),(4888,'A1',1,'2026-06-02 18:54:47',3),(4889,'A2',1,'2026-06-02 18:54:47',3),(4890,'A3',1,'2026-06-02 18:54:47',3),(4891,'A4',1,'2026-06-02 18:54:47',3),(4892,'A5',1,'2026-06-02 18:54:47',3),(4893,'A6',1,'2026-06-02 18:54:47',3),(4894,'A7',1,'2026-06-02 18:54:47',3),(4895,'A8',1,'2026-06-02 18:54:47',3),(4896,'A9',1,'2026-06-02 18:54:47',3),(4897,'A10',1,'2026-06-02 18:54:47',3),(4898,'B1',1,'2026-06-02 18:54:47',3),(4899,'B2',1,'2026-06-02 18:54:47',3),(4900,'B3',1,'2026-06-02 18:54:47',3),(4901,'B4',1,'2026-06-02 18:54:47',3),(4902,'B5',1,'2026-06-02 18:54:47',3),(4903,'B6',1,'2026-06-02 18:54:47',3),(4904,'B7',1,'2026-06-02 18:54:47',3),(4905,'B8',1,'2026-06-02 18:54:47',3),(4906,'B9',1,'2026-06-02 18:54:47',3),(4907,'B10',1,'2026-06-02 18:54:47',3),(4908,'C1',1,'2026-06-02 18:54:47',3),(4909,'C2',1,'2026-06-02 18:54:47',3),(4910,'C3',1,'2026-06-02 18:54:47',3),(4911,'C4',1,'2026-06-02 18:54:47',3),(4912,'C5',1,'2026-06-02 18:54:47',3),(4913,'C6',1,'2026-06-02 18:54:47',3),(4914,'C7',1,'2026-06-02 18:54:47',3),(4915,'C8',1,'2026-06-02 18:54:47',3),(4916,'C9',1,'2026-06-02 18:54:47',3),(4917,'C10',1,'2026-06-02 18:54:47',3),(4918,'D1',1,'2026-06-02 18:54:47',3),(4919,'D2',1,'2026-06-02 18:54:47',3),(4920,'D3',1,'2026-06-02 18:54:47',3),(4921,'D4',1,'2026-06-02 18:54:47',3),(4922,'D5',1,'2026-06-02 18:54:47',3),(4923,'D6',1,'2026-06-02 18:54:47',3),(4924,'D7',1,'2026-06-02 18:54:47',3),(4925,'D8',1,'2026-06-02 18:54:47',3),(4926,'D9',1,'2026-06-02 18:54:47',3),(4927,'D10',1,'2026-06-02 18:54:47',3),(4928,'A1',1,'2026-06-02 19:04:36',7),(4929,'A2',1,'2026-06-02 19:04:36',7),(4930,'A3',1,'2026-06-02 19:04:36',7),(4931,'A4',1,'2026-06-02 19:04:36',7),(4932,'A5',1,'2026-06-02 19:04:36',7),(4933,'A6',1,'2026-06-02 19:04:36',7),(4934,'A7',1,'2026-06-02 19:04:36',7),(4935,'A8',1,'2026-06-02 19:04:36',7),(4936,'A9',1,'2026-06-02 19:04:36',7),(4937,'A10',1,'2026-06-02 19:04:36',7),(4938,'B1',1,'2026-06-02 19:04:36',7),(4939,'B2',1,'2026-06-02 19:04:36',7),(4940,'B3',1,'2026-06-02 19:04:36',7),(4941,'B4',1,'2026-06-02 19:04:36',7),(4942,'B5',1,'2026-06-02 19:04:36',7),(4943,'B6',1,'2026-06-02 19:04:36',7),(4944,'B7',1,'2026-06-02 19:04:36',7),(4945,'B8',1,'2026-06-02 19:04:36',7),(4946,'B9',1,'2026-06-02 19:04:36',7),(4947,'B10',1,'2026-06-02 19:04:36',7),(4970,'A1',1,'2026-06-04 12:24:10',8),(4971,'A2',1,'2026-06-04 12:24:10',8),(4972,'A3',1,'2026-06-04 12:24:10',8),(4973,'A4',1,'2026-06-04 12:24:10',8),(4974,'A5',1,'2026-06-04 12:24:10',8),(4975,'A6',1,'2026-06-04 12:24:10',8),(4976,'A7',1,'2026-06-04 12:24:10',8),(4977,'A8',1,'2026-06-04 12:24:10',8),(4978,'A9',1,'2026-06-04 12:24:10',8),(4979,'A10',1,'2026-06-04 12:24:10',8),(4980,'B1',1,'2026-06-04 12:24:10',8),(5081,'A1',1,'2026-06-04 12:24:32',5),(5082,'A2',1,'2026-06-04 12:24:32',5),(5083,'A3',1,'2026-06-04 12:24:32',5),(5084,'A4',1,'2026-06-04 12:24:32',5),(5085,'A5',1,'2026-06-04 12:24:32',5),(5086,'A6',1,'2026-06-04 12:24:32',5),(5087,'A7',1,'2026-06-04 12:24:32',5),(5088,'A8',1,'2026-06-04 12:24:32',5),(5089,'A9',1,'2026-06-04 12:24:32',5),(5090,'A10',1,'2026-06-04 12:24:32',5),(5091,'B1',1,'2026-06-04 12:24:32',5),(5092,'B2',1,'2026-06-04 12:24:32',5),(5093,'B3',1,'2026-06-04 12:24:32',5),(5094,'B4',1,'2026-06-04 12:24:32',5),(5095,'B5',1,'2026-06-04 12:24:32',5),(5096,'B6',1,'2026-06-04 12:24:32',5),(5097,'B7',1,'2026-06-04 12:24:32',5),(5098,'B8',1,'2026-06-04 12:24:32',5),(5099,'B9',1,'2026-06-04 12:24:32',5),(5100,'B10',1,'2026-06-04 12:24:32',5),(5101,'C1',1,'2026-06-04 12:24:32',5),(5102,'C2',1,'2026-06-04 12:24:32',5),(5103,'C3',1,'2026-06-04 12:24:32',5),(5104,'C4',1,'2026-06-04 12:24:32',5),(5105,'C5',1,'2026-06-04 12:24:32',5),(5106,'C6',1,'2026-06-04 12:24:32',5),(5107,'C7',1,'2026-06-04 12:24:32',5),(5108,'C8',1,'2026-06-04 12:24:32',5),(5109,'C9',1,'2026-06-04 12:24:32',5),(5110,'C10',1,'2026-06-04 12:24:32',5),(5111,'D1',1,'2026-06-04 12:24:32',5),(5112,'D2',1,'2026-06-04 12:24:32',5),(5113,'D3',1,'2026-06-04 12:24:32',5),(5114,'D4',1,'2026-06-04 12:24:32',5),(5115,'D5',1,'2026-06-04 12:24:32',5),(5116,'D6',1,'2026-06-04 12:24:32',5),(5117,'D7',1,'2026-06-04 12:24:32',5),(5118,'D8',1,'2026-06-04 12:24:32',5),(5119,'D9',1,'2026-06-04 12:24:32',5),(5120,'D10',1,'2026-06-04 12:24:32',5),(5121,'E1',1,'2026-06-04 12:24:32',5),(5122,'E2',1,'2026-06-04 12:24:32',5),(5123,'E3',1,'2026-06-04 12:24:32',5),(5124,'E4',1,'2026-06-04 12:24:32',5),(5125,'E5',1,'2026-06-04 12:24:32',5),(5126,'E6',1,'2026-06-04 12:24:32',5),(5127,'E7',1,'2026-06-04 12:24:32',5),(5128,'E8',1,'2026-06-04 12:24:32',5),(5129,'E9',1,'2026-06-04 12:24:32',5),(5130,'E10',1,'2026-06-04 12:24:32',5),(5131,'F1',1,'2026-06-04 12:24:32',5),(5132,'F2',1,'2026-06-04 12:24:32',5),(5133,'F3',1,'2026-06-04 12:24:32',5),(5134,'F4',1,'2026-06-04 12:24:32',5),(5135,'F5',1,'2026-06-04 12:24:32',5),(5136,'F6',1,'2026-06-04 12:24:32',5),(5137,'F7',1,'2026-06-04 12:24:32',5),(5138,'F8',1,'2026-06-04 12:24:32',5),(5139,'F9',1,'2026-06-04 12:24:32',5),(5140,'F10',1,'2026-06-04 12:24:32',5),(5141,'G1',1,'2026-06-04 12:24:32',5),(5142,'G2',1,'2026-06-04 12:24:32',5),(5143,'G3',1,'2026-06-04 12:24:32',5),(5144,'G4',1,'2026-06-04 12:24:32',5),(5145,'G5',1,'2026-06-04 12:24:32',5),(5146,'G6',1,'2026-06-04 12:24:32',5),(5147,'G7',1,'2026-06-04 12:24:32',5),(5148,'G8',1,'2026-06-04 12:24:32',5),(5149,'G9',1,'2026-06-04 12:24:32',5),(5150,'G10',1,'2026-06-04 12:24:32',5),(5151,'H1',1,'2026-06-04 12:24:32',5),(5152,'H2',1,'2026-06-04 12:24:32',5),(5153,'H3',1,'2026-06-04 12:24:32',5),(5154,'H4',1,'2026-06-04 12:24:32',5),(5155,'H5',1,'2026-06-04 12:24:32',5),(5156,'H6',1,'2026-06-04 12:24:32',5),(5157,'H7',1,'2026-06-04 12:24:32',5),(5158,'H8',1,'2026-06-04 12:24:32',5),(5159,'H9',1,'2026-06-04 12:24:32',5),(5160,'H10',1,'2026-06-04 12:24:32',5),(5161,'I1',1,'2026-06-04 12:24:32',5),(5162,'I2',1,'2026-06-04 12:24:32',5),(5163,'I3',1,'2026-06-04 12:24:32',5),(5164,'I4',1,'2026-06-04 12:24:32',5),(5165,'I5',1,'2026-06-04 12:24:32',5),(5166,'I6',1,'2026-06-04 12:24:32',5),(5167,'I7',1,'2026-06-04 12:24:32',5),(5168,'I8',1,'2026-06-04 12:24:32',5),(5169,'I9',1,'2026-06-04 12:24:32',5),(5170,'I10',1,'2026-06-04 12:24:32',5),(5171,'J1',1,'2026-06-04 12:24:32',5),(5172,'J2',1,'2026-06-04 12:24:32',5),(5173,'J3',1,'2026-06-04 12:24:32',5),(5174,'J4',1,'2026-06-04 12:24:32',5),(5175,'J5',1,'2026-06-04 12:24:32',5),(5176,'J6',1,'2026-06-04 12:24:32',5),(5177,'J7',1,'2026-06-04 12:24:32',5),(5178,'J8',1,'2026-06-04 12:24:32',5),(5179,'J9',1,'2026-06-04 12:24:32',5),(5180,'J10',1,'2026-06-04 12:24:32',5),(5181,'A1',1,'2026-06-04 12:24:48',10),(5182,'A2',1,'2026-06-04 12:24:48',10),(5183,'A3',1,'2026-06-04 12:24:48',10),(5184,'A4',1,'2026-06-04 12:24:48',10),(5185,'A5',1,'2026-06-04 12:24:48',10),(5186,'A6',1,'2026-06-04 12:24:48',10),(5187,'A7',1,'2026-06-04 12:24:48',10),(5188,'A8',1,'2026-06-04 12:24:48',10),(5189,'A9',1,'2026-06-04 12:24:48',10),(5190,'A10',1,'2026-06-04 12:24:48',10),(5191,'B1',1,'2026-06-04 12:24:48',10),(5192,'B2',1,'2026-06-04 12:24:48',10),(5193,'B3',1,'2026-06-04 12:24:48',10),(5194,'B4',1,'2026-06-04 12:24:48',10),(5195,'B5',1,'2026-06-04 12:24:48',10),(5196,'B6',1,'2026-06-04 12:24:48',10),(5197,'B7',1,'2026-06-04 12:24:48',10),(5198,'B8',1,'2026-06-04 12:24:48',10),(5199,'B9',1,'2026-06-04 12:24:48',10),(5200,'B10',1,'2026-06-04 12:24:48',10),(5201,'C1',1,'2026-06-04 12:24:48',10),(5202,'C2',1,'2026-06-04 12:24:48',10),(5203,'A1',1,'2026-06-04 12:25:00',9),(5204,'A2',1,'2026-06-04 12:25:00',9),(5205,'A3',1,'2026-06-04 12:25:00',9),(5206,'A4',1,'2026-06-04 12:25:00',9),(5207,'A5',1,'2026-06-04 12:25:00',9),(5208,'A6',1,'2026-06-04 12:25:00',9),(5209,'A7',1,'2026-06-04 12:25:00',9),(5210,'A8',1,'2026-06-04 12:25:00',9),(5211,'A9',1,'2026-06-04 12:25:00',9),(5212,'A10',1,'2026-06-04 12:25:00',9),(5213,'B1',1,'2026-06-04 12:25:00',9),(5214,'B2',1,'2026-06-04 12:25:00',9),(5215,'B3',1,'2026-06-04 12:25:00',9),(5216,'B4',1,'2026-06-04 12:25:00',9),(5217,'B5',1,'2026-06-04 12:25:00',9),(5218,'B6',1,'2026-06-04 12:25:00',9),(5219,'B7',1,'2026-06-04 12:25:00',9),(5220,'B8',1,'2026-06-04 12:25:00',9),(5221,'B9',1,'2026-06-04 12:25:00',9),(5222,'B10',1,'2026-06-04 12:25:00',9),(5223,'C1',1,'2026-06-04 12:25:00',9),(5224,'C2',1,'2026-06-04 12:25:00',9);
/*!40000 ALTER TABLE `seats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `showtimes`
--

DROP TABLE IF EXISTS `showtimes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `showtimes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `movie_id` int NOT NULL,
  `room_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_showtime_movie` (`movie_id`),
  KEY `fk_showtime_room` (`room_id`),
  KEY `idx_showtime_time` (`start_time`,`end_time`),
  CONSTRAINT `fk_showtime_movie` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_showtime_room` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `showtimes`
--

LOCK TABLES `showtimes` WRITE;
/*!40000 ALTER TABLE `showtimes` DISABLE KEYS */;
INSERT INTO `showtimes` VALUES (1,'2026-06-01 09:00:00','2026-06-01 10:55:00','2026-05-29 13:18:49',4,2),(2,'2026-06-01 13:00:00','2026-06-01 15:18:00','2026-05-29 13:18:49',1,2),(3,'2026-06-01 16:00:00','2026-06-01 18:05:00','2026-05-29 13:18:49',2,1),(4,'2026-06-01 19:30:00','2026-06-01 21:50:00','2026-05-29 13:18:49',2,1),(5,'2026-06-01 20:00:00','2026-06-01 21:50:00','2026-05-29 13:18:49',3,4),(6,'2026-06-01 22:30:00','2026-06-01 00:20:00','2026-05-29 13:18:49',3,4),(7,'2026-06-04 09:00:00','2026-06-04 10:55:00','2026-06-04 09:25:31',1,1),(8,'2026-06-04 13:00:00','2026-06-04 15:18:00','2026-06-04 09:25:31',1,1),(9,'2026-06-04 16:00:00','2026-06-04 18:05:00','2026-06-04 09:25:31',1,2),(10,'2026-06-04 19:30:00','2026-06-04 21:50:00','2026-06-04 09:25:31',2,2);
/*!40000 ALTER TABLE `showtimes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES (1,'Active','Room available','2026-05-29 13:15:51'),(2,'Maintenance','Room under maintenance','2026-05-29 13:15:51'),(3,'Closed','Room closed','2026-05-29 13:15:51');
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status_movie`
--

DROP TABLE IF EXISTS `status_movie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `status_movie` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name_status` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status_movie`
--

LOCK TABLES `status_movie` WRITE;
/*!40000 ALTER TABLE `status_movie` DISABLE KEYS */;
INSERT INTO `status_movie` VALUES (1,'Now Showing'),(2,'Coming Soon'),(3,'Stopped');
/*!40000 ALTER TABLE `status_movie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `price` float NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `booking_id` int NOT NULL,
  `seat_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ticket_booking` (`booking_id`),
  KEY `fk_ticket_seat` (`seat_id`),
  CONSTRAINT `fk_ticket_booking` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ticket_seat` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
INSERT INTO `tickets` VALUES (1,120000,'2026-06-01 08:53:13',1,1),(2,120000,'2026-06-01 08:53:13',2,2),(3,95000,'2026-06-01 08:53:13',3,3),(4,90000,'2026-06-01 08:53:13',4,6),(5,90000,'2026-06-01 08:53:13',5,7);
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT 'ROLE_USER',
  `avatar` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `approved` tinyint(1) DEFAULT '1',
  `number_phone` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Administrator','admin','$2a$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_ADMIN',NULL,1,1,NULL,'2026-05-29 13:15:51'),(2,'Nguyễn Văn Khách','customer1','$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_USER','avatar1.png',1,1,'0901234567','2026-05-29 13:18:49'),(3,'Trần Thị Bình','customer2','$2a$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_USER','avatar2.png',1,1,'0912345678','2026-05-29 13:18:49'),(4,'Lê Minh Thống','staff1','$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_STAFF','avatar3.png',1,1,'0923456789','2026-05-29 13:18:49'),(5,'Phạm Hồng Nhung','customer3','$2a$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_USER','avatar4.png',1,1,'0934567890','2026-05-29 13:18:49'),(6,'Bùi Hoàng Long','customer4','$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_USER',NULL,1,1,'0945678901','2026-05-29 13:18:49'),(7,'nguyen','dat','$2a$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_CUSTOMER',NULL,1,1,'','2026-05-29 13:54:10'),(8,'nguyen ','dat1','$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_CUSTOMER',NULL,1,1,'','2026-05-29 16:05:08'),(9,'nguyen','admin1','$2a$10$HdeDVteNHYjAHSPNRLtDXeiWUEbzBLixtj/4AkF8Npr0obYQqcOyi','ROLE_ADMIN',NULL,1,1,NULL,'2026-05-29 16:09:44'),(10,'nguen','staff3','$2a$10$Hy4n7427mz1rHs2VzYJbQO/pRbbhqMQP2reJvcb/jm8FIIvN2xHe.','ROLE_STAFF',NULL,1,1,'','2026-06-01 10:17:00'),(11,'ngueyn','staff4','$2a$10$4AuzpyPT7TLI1JNNMt.va.o29Nzuk0qtW8ZqcLn8ni.kfEKByjanq','ROLE_CUSTOMER',NULL,1,1,'','2026-06-01 15:23:02'),(12,'à','staff5','$2a$10$LP19DpkUiM6cwd.54LdIy.R9XCgD5Y4qAXHjYWNAAw1qsx1PH3/2G','ROLE_STAFF',NULL,0,1,'','2026-06-01 15:23:32'),(13,'Hòa Từ','staff2','$2a$10$ehCcdGXp2KJY3Oq9ZERbOeAL..eLwc31yTCMXfKlje0OpY16tZPCS','ROLE_STAFF','https://res.cloudinary.com/dxxwcby8l/image/upload/v1780551328/mf9oirglemhvwkqx6z17.jpg',1,0,'0703172549','2026-06-04 12:35:24');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'dbcenima'
--

--
-- Dumping routines for database 'dbcenima'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-27 21:13:26
