DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS result;
DROP TABLE IF EXISTS settings;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE result (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, --创建时间
  score INTEGER NOT NULL, -- 得分
  machine TEXT, -- 机器名称
  title TEXT NOT NULL, -- 题目
  gray_banlance REAL NOT NULL, -- 灰平衡彩度差
  cyan_expend REAL NOT NULL, -- 青网扩
  cyan_density REAL NOT NULL, -- 青密度
  cyan_difference REAL NOT NULL, -- 青色色差
  magenta_expend REAL NOT NULL, -- 品网扩
  magenta_density REAL NOT NULL, -- 品密度
  magenta_difference REAL NOT NULL, -- 品色色差
  yellow_expend REAL NOT NULL, -- 黄网扩
  yellow_density REAL NOT NULL, -- 黄密度
  yellow_difference REAL NOT NULL, -- 黄色色差
  black_expend REAL NOT NULL, -- 黑网扩
  black_density REAL NOT NULL, -- 黑密度
  black_difference REAL NOT NULL, -- 黑色色差
  header_M REAL NOT NULL, -- 报头M密度
  header_Y REAL NOT NULL, -- 报头Y密度
  header_difference REAL NOT NULL, -- 报头色差
  middle_expend REAL NOT NULL, -- 中间调扩展值
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  author_id INTEGER NOT NULL,
  header_L REAL NOT NULL,
  header_a REAL NULL NULL,
  header_b REAL NOT NULL,
  header_magenta REAL NOT NULL,
  header_yellow REAL NOT NULL,
  cyan_standard REAL NOT NULL,
  magenta_standard REAL NOT NULL,
  yellow_standard REAL NOT NULL,
  black_standard REAL NOT NULL,
  cyan_expend REAL NOT NULL,
  magenta_expend REAL NOT NULL,
  yellow_expend REAL NOT NULL,
  black_expend REAL NOT NULL,
  cyan_L REAL NOT NULL,
  cyan_a REAL NOT NULL,
  cyan_b REAL NOT NULL,
  magenta_L REAL NOT NULL,
  magenta_a REAL NOT NULL,
  magenta_b REAL NOT NULL,
  yellow_L REAL NOT NULL,
  yellow_a REAL NOT NULL,
  yellow_b REAL NOT NULL,
  black_L REAL NOT NULL,
  black_a REAL NOT NULL,
  black_b REAL NOT NULL,
  header_density_difference REAL NOT NULL,
  header_difference REAL NOT NULL,
  middle_expend REAL NOT NULL,
  four_expend REAL NOT NULL,
  field_density REAL NOT NULL, -- 实地密度
  field_density_consistency REAL, --实地密度一致性
  four_defference REAL NOT NULL, --四色色差
  gray_banlance REAL NOT NULL,
  de_standard REAL NOT NULL, --的字的标准密度
  ink_number REAL NOT NULL, --对开墨条数
  FOREIGN KEY (author_id) REFERENCES user (id)
);