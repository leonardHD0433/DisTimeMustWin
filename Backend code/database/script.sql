/****** Object:  Database [url_database]    Script Date: 30/6/2024 3:15:33 PM ******/
CREATE DATABASE [url_database]  (EDITION = 'GeneralPurpose', SERVICE_OBJECTIVE = 'GP_S_Gen5_2', MAXSIZE = 32 GB) WITH CATALOG_COLLATION = SQL_Latin1_General_CP1_CI_AS, LEDGER = OFF;
GO
ALTER DATABASE [url_database] SET COMPATIBILITY_LEVEL = 160
GO
ALTER DATABASE [url_database] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [url_database] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [url_database] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [url_database] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [url_database] SET ARITHABORT OFF 
GO
ALTER DATABASE [url_database] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [url_database] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [url_database] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [url_database] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [url_database] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [url_database] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [url_database] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [url_database] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [url_database] SET ALLOW_SNAPSHOT_ISOLATION ON 
GO
ALTER DATABASE [url_database] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [url_database] SET READ_COMMITTED_SNAPSHOT ON 
GO
ALTER DATABASE [url_database] SET  MULTI_USER 
GO
ALTER DATABASE [url_database] SET ENCRYPTION ON
GO
ALTER DATABASE [url_database] SET QUERY_STORE = ON
GO
ALTER DATABASE [url_database] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 100, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
/*** The scripts of database scoped configurations in Azure should be executed inside the target database connection. ***/
GO
-- ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP = 8;
GO
/****** Object:  Table [dbo].[URL]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[URL](
	[url] [varchar](max) NOT NULL,
	[type] [nvarchar](50) NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[List Phishing]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[List Phishing] AS
SELECT *
FROM URL
WHERE type = 'phishing';
GO
/****** Object:  View [dbo].[List Benign]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[List Benign] AS
SELECT *
FROM URL
WHERE type = 'benign';
GO
/****** Object:  View [dbo].[List Defacement]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[List Defacement] AS
SELECT *
FROM URL
WHERE type = 'defacement';
GO
/****** Object:  View [dbo].[List Malware]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[List Malware] AS SELECT * FROM URL WHERE type='malware';
GO
/****** Object:  View [dbo].[List Unsecure]    Script Date: 30/6/2024 3:15:33 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[List Unsecure] AS SELECT * FROM URL WHERE type='unsecure';
GO
ALTER DATABASE [url_database] SET  READ_WRITE 
GO
