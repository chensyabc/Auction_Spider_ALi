CREATE DATABASE IF NOT EXISTS Auction_Spider_ALi;
USE Auction_Spider_ALi;

DROP TABLE IF EXISTS Auctions;
CREATE TABLE IF NOT EXISTS Auctions
(
  `Id` INT AUTO_INCREMENT,
  `AuctionId` VARCHAR(14) NOT NULL,
  `CourtId` VARCHAR(20) NOT NULL,
  `Title` VARCHAR(100) NOT NULL,
  `CategoryId` INT NOT NULL,
  `Url` VARCHAR(80) NOT NULL,
  `StartPrice` DECIMAL(18,2) NOT NULL,
  `CurrentPrice` DECIMAL(18,2) NOT NULL,
  `CashDeposit` VARCHAR(80) DEFAULT NULL,
  `PaymentAdvance` VARCHAR(80) DEFAULT NULL,
  `AccessPrice` DECIMAL(18,2) DEFAULT NULL,
  `FareIncrease` DECIMAL(18,2) DEFAULT NULL,
  `AuctionTimes` VARCHAR(10) DEFAULT NULL,
  `AuctionType` VARCHAR(20) DEFAULT NULL,
  `DelayCycle` VARCHAR(80) DEFAULT NULL,
  `CorporateAgent` VARCHAR(30) DEFAULT NULL,
  `Phone` VARCHAR(50) DEFAULT NULL,
  `SellingPeriod` VARCHAR(30) DEFAULT NULL,
  `OnlineCycle` VARCHAR(10) DEFAULT NULL,
  `BiddingRecord` VARCHAR(10) DEFAULT NULL,
  `AuctionModel` VARCHAR(10) DEFAULT NULL,
  `Enrollment` VARCHAR(10) DEFAULT NULL,
  `SetReminders` INT DEFAULT NULL,
  `Onlookers` VARCHAR(10) DEFAULT NULL,
  `CreatedOn` DATETIME DEFAULT NULL,
  `UpdatedOn` DATETIME DEFAULT NULL,
  `StatusId` INT NOT NULL,
  `SpiderStatusId` INT NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Auctions_History;
CREATE TABLE IF NOT EXISTS Auctions_History
(
  `Id` INT AUTO_INCREMENT,
  `AuctionId` VARCHAR(14) NOT NULL,
  `CourtId` INT NOT NULL,
  `Title` VARCHAR(100) NOT NULL,
  `CategoryId` INT NOT NULL,
  `Url` VARCHAR(80) NOT NULL,
  `StartPrice` DECIMAL NOT NULL,
  `CurrentPrice` DECIMAL NOT NULL,
  `CashDeposit` VARCHAR(80) DEFAULT NULL,
  `PaymentAdvance` VARCHAR(80) DEFAULT NULL,
  `AccessPrice` DECIMAL DEFAULT NULL,
  `FareIncrease` DECIMAL DEFAULT NULL,
  `AuctionTimes` VARCHAR(10) DEFAULT NULL,
  `AuctionType` VARCHAR(20) DEFAULT NULL,
  `DelayCycle` VARCHAR(80) DEFAULT NULL,
  `CorporateAgent` VARCHAR(30) DEFAULT NULL,
  `Phone` VARCHAR(50) DEFAULT NULL,
  `SellingPeriod` VARCHAR(30) DEFAULT NULL,
  `OnlineCycle` VARCHAR(10) DEFAULT NULL,
  `BiddingRecord` VARCHAR(10) DEFAULT NULL,
  `AuctionModel` VARCHAR(10) DEFAULT NULL,
  `Enrollment` VARCHAR(10) DEFAULT NULL,
  `SetReminders` INT DEFAULT NULL,
  `Onlookers` VARCHAR(10) DEFAULT NULL,
  `CreatedOn` DATE DEFAULT NULL,
  `UpdatedOn` DATE DEFAULT NULL,
  `StatusId` INT NOT NULL,
  `SpiderStatusId` INT NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Auction_Categories;
CREATE TABLE IF NOT EXISTS Auction_Categories
(
  `Id` INT AUTO_INCREMENT,
  `CategoryId` VARCHAR(10) NOT NULL,
  `CategoryName` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Auction_Statuses;
CREATE TABLE IF NOT EXISTS Auction_Statuses
(
  `Id` INT AUTO_INCREMENT,
  `StatusId` INT NOT NULL,
  `StatusName` VARCHAR(15) NOT NULL,
  `IsSpiderThisStatus` TINYINT(1) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Auction_History_Statuses;
CREATE TABLE IF NOT EXISTS Auction_History_Statuses
(
  `Id` INT AUTO_INCREMENT,
  `StatusId` INT NOT NULL,
  `StatusName` VARCHAR(15) NOT NULL,
  `IsSpiderThisStatus` TINYINT(1) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Courts;
CREATE TABLE IF NOT EXISTS Courts
(
  `Id` INT AUTO_INCREMENT,
  `CourtCityId` VARCHAR(10) NOT NULL,
  `CourtSubId` VARCHAR(5) NOT NULL,
  `CourtId` VARCHAR(50) NOT NULL,
  `CourtName` VARCHAR(60) NOT NULL,
  `City` VARCHAR(60) DEFAULT NULL,
  `Province` VARCHAR(60) DEFAULT NULL,
  `AuctionCount` INT NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Auction_Processes;
CREATE TABLE IF NOT EXISTS Auction_Processes
(
  `Id` INT AUTO_INCREMENT,
  `URL` VARCHAR(1000) NOT NULL,
  `IsFinished` BIT NOT NULL,
  `CreatedOn` DATETIME NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO Auction_Statuses(StatusId, StatusName, IsSpiderThisStatus)
    SELECT 0, N'正在进行', 1
    UNION SELECT 1, N'即将开始', 1
    UNION SELECT 2, N'已结束', 0
    UNION SELECT 4, N'中止', 0
    UNION SELECT 5, N'撤回', 0

INSERT INTO Auction_History_Statuses(StatusId, StatusName, IsSpiderThisStatus)
    SELECT 0, N'正在进行', 0
    UNION SELECT 1, N'即将开始', 0
    UNION SELECT 2, N'已结束', 1
    UNION SELECT 4, N'中止', 1
    UNION SELECT 5, N'撤回', 1

INSERT INTO auction_categories(CategoryId, CategoryName)
    SELECT 50025969, N'住宅用房'
    UNION SELECT 200782003, N'住宅用房'
    UNION SELECT 200788003, N'工业用房'
    UNION SELECT 378, N'机动车'
    UNION SELECT 379, N'其他'
    UNION SELECT 380, N'工艺品'
    UNION SELECT 381, N'土地'
    UNION SELECT 383, N'船舶'
    UNION SELECT 385, N'无形资产'
    UNION SELECT 386, N'财产性权益'

CREATE VIEW Auction_Analysis
AS
(
	SELECT 	CurrentPrice AS CurrentPrice_MoveForward
					, AccessPrice AS AccessPrice_MoveForward
					, AccessPrice-CurrentPrice AS PriceDiffer
					, CONCAT(CAST(CAST(100*(AccessPrice-CurrentPrice)/CurrentPrice AS DECIMAL(18,2)) AS CHAR), '%') AS PriceDifferRate
					, au.*
	FROM 		auctions au
	ORDER BY (AccessPrice-CurrentPrice)/AccessPrice DESC
);
