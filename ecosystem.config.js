module.exports = {
    apps : [{
      name: "AceTaffy-Weibo",
      script: "./app.py",
      interpreter: "python",
      args: '0',
      autorestart: true,
      watch: false,
      pid_file: './weibo.pid',
      time: true,
      log_date_format : "YYYY-MM-DD HH:mm Z",
      // log_type: 'json',
      log_rotate: true,
      log_max_size: '10M',
      log_max_files: 10,
      log_symlink: true,
    }]
  }
  