#!/usr/bin/env python3
"""Build the rewritten index.html for property-quiz"""

# Read the questions data from the current file
with open('/home/user/property-quiz/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract questions array (from "const questions = [" to the closing "];")
start = content.index('const questions = [')
# Find the end - the ]; that closes the questions array
# We know it ends around line 1992
end_search_start = content.index('answer: `主要包括：事故或险情发生后的即时处置', start)
end = content.index('\n        ];', end_search_start) + len('\n        ];')

questions_block = content[start:end]

# Extract chapters block
ch_start = content.index('const chapters = [')
ch_end = content.index('\n        ];', ch_start) + len('\n        ];')
chapters_block = content[ch_start:ch_end]

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>物业初级操作题刷题</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        :root {
            --primary: #1890ff;
            --success: #52c41a;
            --error: #ff4d4f;
            --bg: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333;
            --text-light: #666;
            --border: #e8e8e8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg); color: var(--text); min-height: 100vh;
            padding-bottom: 70px; overflow-x: hidden;
        }
        .header {
            background: var(--primary); color: white; padding: 16px 20px;
            position: sticky; top: 0; z-index: 100;
            box-shadow: 0 2px 8px rgba(24,144,255,0.3);
        }
        .header h1 { font-size: 18px; font-weight: 600; }
        .header-sub { font-size: 12px; opacity: 0.9; margin-top: 4px; }
        .page { display: none; padding: 16px; animation: fadeIn 0.3s ease; }
        .page.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .card { background: var(--card-bg); border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .home-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
        .stat-item { background: linear-gradient(135deg, var(--primary), #40a9ff); color: white; padding: 16px; border-radius: 12px; text-align: center; }
        .stat-item.green { background: linear-gradient(135deg, var(--success), #73d13d); }
        .stat-item.orange { background: linear-gradient(135deg, #fa8c16, #ffc53d); }
        .stat-value { font-size: 28px; font-weight: 700; }
        .stat-label { font-size: 12px; opacity: 0.9; margin-top: 4px; }
        .btn {
            display: block; width: 100%; padding: 16px; border: none; border-radius: 12px;
            font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; margin-bottom: 12px;
        }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:active { background: #096dd9; transform: scale(0.98); }
        .btn-outline { background: white; color: var(--primary); border: 2px solid var(--primary); }
        .btn-outline:active { background: #e6f7ff; }
        .btn-redo { background: white; color: #fa8c16; border: 2px solid #fa8c16; }
        .btn-redo:active { background: #fff7e6; transform: scale(0.98); }
        .btn-danger { background: white; color: var(--error); border: 2px solid var(--error); }
        .btn-danger:active { background: #fff2f0; }

        /* 章节列表 */
        .chapter-list { list-style: none; }
        .chapter-item {
            display: flex; align-items: center; padding: 16px; background: white;
            border-radius: 12px; margin-bottom: 12px; cursor: pointer;
            transition: all 0.3s; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }
        .chapter-item:active { transform: scale(0.98); background: #f5f5f5; }
        .chapter-icon {
            width: 48px; height: 48px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 20px; margin-right: 14px; flex-shrink: 0;
        }
        .chapter-icon.ch3 { background: linear-gradient(135deg, #1890ff, #40a9ff); }
        .chapter-icon.ch4 { background: linear-gradient(135deg, #722ed1, #9254de); }
        .chapter-icon.ch5 { background: linear-gradient(135deg, #13c2c2, #36cfc9); }
        .chapter-icon.ch6 { background: linear-gradient(135deg, #fa8c16, #ffc53d); }
        .chapter-icon.ch8 { background: linear-gradient(135deg, #eb2f96, #f759ab); }
        .chapter-info { flex: 1; min-width: 0; }
        .chapter-title { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
        .chapter-meta { font-size: 12px; color: var(--text-light); }
        .chapter-progress { width: 100%; height: 6px; background: #f0f0f0; border-radius: 3px; margin-top: 8px; overflow: hidden; }
        .chapter-progress-fill { height: 100%; background: var(--primary); border-radius: 3px; transition: width 0.3s; }
        .chapter-arrow { color: #ccc; font-size: 18px; margin-left: 8px; }
        .page-back {
            display: inline-flex; align-items: center; gap: 4px;
            font-size: 14px; color: var(--primary); background: none; border: none;
            padding: 8px 0; margin-bottom: 12px; cursor: pointer;
        }

        /* 答题页面 */
        .question-page {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: var(--bg); z-index: 200; display: none; flex-direction: column;
        }
        .question-page.active { display: flex; }
        .question-header {
            background: white; padding: 12px 16px;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid var(--border); flex-shrink: 0;
        }
        .question-back { font-size: 16px; color: var(--primary); background: none; border: none; padding: 8px; margin: -8px; cursor: pointer; }
        .question-progress { font-size: 14px; color: var(--text-light); }
        .star-btn { background: none; border: none; font-size: 20px; color: #ccc; cursor: pointer; padding: 4px; }
        .star-btn.starred { color: #faad14; }
        .exam-progress-bar { display: none; background: #f0f0f0; border-radius: 4px; height: 6px; margin: 0 16px; overflow: hidden; }
        .exam-progress-bar.show { display: block; }
        .exam-progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), #40a9ff); border-radius: 4px; transition: width 0.3s; }
        .question-content { flex: 1; overflow-y: auto; padding: 16px; -webkit-overflow-scrolling: touch; }
        .question-type {
            display: inline-block; padding: 4px 12px; background: #e6f7ff;
            color: var(--primary); border-radius: 20px; font-size: 12px; margin-bottom: 12px;
        }
        .exam-score-label {
            display: none; font-size: 13px; color: var(--primary); font-weight: 600;
            margin-bottom: 8px; padding: 6px 12px; background: #e6f7ff;
            border-radius: 8px; text-align: center;
        }
        .exam-score-label.show { display: block; }
        .question-context {
            background: #fffbe6; border: 1px solid #ffe58f; border-radius: 8px;
            padding: 12px; font-size: 14px; line-height: 1.6; color: #ad6800; margin-bottom: 16px;
            white-space: pre-wrap;
        }
        .question-text { font-size: 17px; line-height: 1.7; color: var(--text); margin-bottom: 20px; white-space: pre-wrap; }
        .input-area { margin-bottom: 16px; }
        .input-area textarea {
            width: 100%; min-height: 120px; padding: 14px; border: 2px solid var(--border);
            border-radius: 12px; font-size: 16px; line-height: 1.6; resize: vertical; transition: border-color 0.3s;
        }
        .input-area textarea:focus { outline: none; border-color: var(--primary); }
        .user-answer-display {
            background: #f0f5ff; border: 1px solid #adc6ff; border-radius: 8px;
            padding: 12px; font-size: 15px; line-height: 1.6; color: #2f54eb;
            margin-bottom: 16px; display: none; white-space: pre-wrap;
        }
        .answer-section {
            background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 12px;
            padding: 16px; margin-top: 16px; display: none;
        }
        .answer-section.show { display: block; animation: slideUp 0.3s ease; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .answer-title { font-size: 14px; color: var(--success); font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; }
        .answer-title::before { content: "✓"; margin-right: 6px; font-weight: bold; }
        .answer-text { font-size: 15px; line-height: 1.7; color: #389e0d; white-space: pre-wrap; }
        .feedback { text-align: center; padding: 20px; border-radius: 12px; margin-bottom: 16px; display: none; }
        .feedback.show { display: block; animation: bounce 0.5s ease; }
        @keyframes bounce { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        .feedback.correct { background: #f6ffed; border: 2px solid var(--success); }
        .feedback.wrong { background: #fff2f0; border: 2px solid var(--error); }
        .feedback-icon { font-size: 48px; margin-bottom: 10px; }
        .feedback-text { font-size: 16px; font-weight: 600; line-height: 1.5; }
        .btn-group { display: flex; gap: 12px; padding: 16px; background: white; border-top: 1px solid var(--border); flex-shrink: 0; }
        .btn-group .btn { flex: 1; margin: 0; }

        /* 底部导航 */
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0; background: white;
            display: flex; border-top: 1px solid var(--border); z-index: 100; padding: 8px 0;
            padding-bottom: max(8px, env(safe-area-inset-bottom));
        }
        .nav-item { flex: 1; text-align: center; padding: 6px; cursor: pointer; color: var(--text-light); transition: color 0.3s; }
        .nav-item.active { color: var(--primary); }
        .nav-icon { font-size: 22px; margin-bottom: 2px; }
        .nav-label { font-size: 11px; }

        /* 错题列表 */
        .wrong-list { list-style: none; }
        .wrong-item {
            background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px;
            cursor: pointer; transition: all 0.3s; border-left: 4px solid var(--error);
        }
        .wrong-item:active { transform: scale(0.98); }
        .wrong-title { font-size: 14px; color: var(--text); margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .wrong-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-light); }
        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-light); }
        .empty-icon { font-size: 64px; margin-bottom: 16px; opacity: 0.5; }

        /* 考试成绩单 */
        .exam-transcript {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: var(--bg); z-index: 300; display: none; flex-direction: column; overflow-y: auto;
        }
        .exam-transcript.show { display: flex; }
        .transcript-header { background: linear-gradient(135deg, #1890ff, #40a9ff); color: white; padding: 30px 20px; text-align: center; flex-shrink: 0; }
        .transcript-header h2 { font-size: 22px; margin-bottom: 8px; }
        .transcript-total { font-size: 48px; font-weight: 700; margin: 10px 0; }
        .transcript-total small { font-size: 20px; font-weight: 400; opacity: 0.8; }
        .transcript-summary { display: flex; justify-content: space-around; padding: 16px 0; margin-bottom: 8px; }
        .transcript-summary-item { text-align: center; }
        .transcript-summary-value { font-size: 24px; font-weight: 700; }
        .transcript-summary-label { font-size: 12px; color: rgba(255,255,255,0.8); margin-top: 4px; }
        .transcript-body { padding: 16px; flex: 1; }
        .transcript-chapter { background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .transcript-chapter-title { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
        .transcript-item { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
        .transcript-item:last-child { border-bottom: none; }
        .transcript-item-index { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; margin-right: 12px; flex-shrink: 0; }
        .transcript-item-index.pass { background: #f6ffed; color: var(--success); }
        .transcript-item-index.fail { background: #fff2f0; color: var(--error); }
        .transcript-item-q { flex: 1; font-size: 14px; color: var(--text); display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; margin-right: 12px; }
        .transcript-item-score { font-size: 16px; font-weight: 600; flex-shrink: 0; }
        .transcript-item-score.pass { color: var(--success); }
        .transcript-item-score.fail { color: var(--error); }
        .transcript-item-max { font-size: 12px; color: var(--text-light); flex-shrink: 0; margin-left: 2px; }
        .transcript-actions { padding: 16px; padding-bottom: max(16px, env(safe-area-inset-bottom)); flex-shrink: 0; }
        .transcript-actions .btn { margin-bottom: 12px; }

        /* AI评分loading */
        .ai-scoring-loading { text-align: center; padding: 20px; }
        .ai-scoring-loading .spinner { display: inline-block; width: 32px; height: 32px; border: 3px solid #f0f0f0; border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .ai-scoring-loading p { margin-top: 10px; font-size: 14px; color: var(--text-light); }

        /* Toast */
        .toast {
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.75); color: white; padding: 12px 24px;
            border-radius: 8px; font-size: 14px; z-index: 1000; opacity: 0;
            transition: opacity 0.3s; pointer-events: none;
        }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>
    <!-- 头部 -->
    <div class="header">
        <h1>物业经理初级刷题</h1>
        <div class="header-sub">2026年第一轮实操考试复习</div>
    </div>

    <!-- 首页 -->
    <div id="page-home" class="page active">
        <div class="card">
            <div class="home-stats">
                <div class="stat-item"><div class="stat-value" id="stat-total">0</div><div class="stat-label">总题数</div></div>
                <div class="stat-item green"><div class="stat-value" id="stat-correct">0</div><div class="stat-label">正确数</div></div>
                <div class="stat-item orange"><div class="stat-value" id="stat-today">0</div><div class="stat-label">今日已答</div></div>
                <div class="stat-item"><div class="stat-value" id="stat-rate">0%</div><div class="stat-label">正确率</div></div>
            </div>
        </div>
        <button class="btn btn-primary" onclick="startDailyPractice()">📝 每日刷题</button>
        <button class="btn btn-outline" onclick="showPage('chapter')">📚 按章节练习</button>
        <button class="btn btn-primary" onclick="startExamPractice()" style="background: linear-gradient(135deg, #722ed1, #9254de);">🎯 模拟考试</button>
    </div>

    <!-- 章节选择页 -->
    <div id="page-chapter" class="page">
        <button class="page-back" onclick="showPage('home')">← 返回首页</button>
        <ul class="chapter-list" id="chapter-list"></ul>
    </div>

    <!-- 错题本页面 -->
    <div id="page-wrong" class="page">
        <button class="btn btn-outline" id="wrong-practice-all-btn" onclick="startWrongPractice()" style="display:none; margin-bottom:16px;">📝 练习全部错题</button>
        <div id="wrong-list-container"></div>
    </div>

    <!-- 答题页面 -->
    <div id="question-page" class="question-page">
        <div class="question-header">
            <button class="question-back" onclick="closeQuestion()">← 返回</button>
            <div class="question-progress" id="question-progress">1/10</div>
            <button class="star-btn" id="star-btn" onclick="toggleStar()">☆</button>
        </div>
        <div class="exam-progress-bar" id="exam-progress-bar">
            <div class="exam-progress-fill" id="exam-progress-fill"></div>
        </div>
        <div class="question-content" id="question-content">
            <div class="question-type" id="question-type">简答题</div>
            <div class="exam-score-label" id="exam-score-label">本题满分：6分</div>
            <div class="question-context" id="question-context" style="display:none;"></div>
            <div class="question-text" id="question-text"></div>
            <div class="feedback" id="feedback">
                <div class="feedback-icon" id="feedback-icon">✓</div>
                <div class="feedback-text" id="feedback-text">正确!</div>
            </div>
            <div class="input-area" id="input-area">
                <textarea id="user-answer" placeholder="请在此输入你的答案..."></textarea>
            </div>
            <div class="user-answer-display" id="user-answer-display"></div>
            <div class="answer-section" id="answer-section">
                <div class="answer-title">参考答案</div>
                <div class="answer-text" id="answer-text"></div>
            </div>
        </div>
        <div class="btn-group" id="btn-group">
            <button class="btn btn-primary" id="submit-btn" onclick="submitAnswer()">提交答案</button>
            <button class="btn btn-outline" id="prev-btn" onclick="prevQuestion()" style="display:none;">上一题</button>
            <button class="btn btn-outline" id="next-btn" onclick="nextQuestion()" style="display:none;">下一题</button>
            <button class="btn btn-redo" id="redo-btn" onclick="redoCurrentQuestion()" style="display:none;">🔄 重做本题</button>
        </div>
    </div>

    <!-- 考试成绩单 -->
    <div class="exam-transcript" id="exam-transcript">
        <div class="transcript-header">
            <h2>📋 模拟考试成绩单</h2>
            <div class="transcript-total" id="transcript-total">0<small>/100</small></div>
            <div class="transcript-summary">
                <div class="transcript-summary-item">
                    <div class="transcript-summary-value" id="transcript-pass-count" style="color:#b7eb8f;">0</div>
                    <div class="transcript-summary-label">及格题数</div>
                </div>
                <div class="transcript-summary-item">
                    <div class="transcript-summary-value" id="transcript-fail-count" style="color:#ffa39e;">0</div>
                    <div class="transcript-summary-label">不及格题数</div>
                </div>
                <div class="transcript-summary-item">
                    <div class="transcript-summary-value" id="transcript-rate">0%</div>
                    <div class="transcript-summary-label">得分率</div>
                </div>
            </div>
        </div>
        <div class="transcript-body" id="transcript-body"></div>
        <div class="transcript-actions">
            <button class="btn btn-primary" onclick="closeTranscript()">返回首页</button>
            <button class="btn btn-outline" onclick="startExamPractice()">🔄 再考一次</button>
        </div>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav" id="bottom-nav">
        <div class="nav-item active" onclick="showPage('home', this)">
            <div class="nav-icon">🏠</div>
            <div class="nav-label">首页</div>
        </div>
        <div class="nav-item" onclick="showPage('wrong', this)">
            <div class="nav-icon">📝</div>
            <div class="nav-label">错题</div>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast"></div>

    <script>
        // ========== 题目数据 ==========
''' + questions_block + '''

        // ========== 章节信息 ==========
''' + chapters_block + '''

        // ========== 状态管理 ==========
        let currentQuestionIndex = 0;
        let currentQuestions = [];
        let userAnswer = '';
        let hasSubmitted = false;
        let isStarred = false;
        let currentMode = 'chapter'; // 'daily', 'chapter', 'wrong', 'exam'
        let answeredMap = new Map(); // key: question.id, value: { userAnswer, score, maxScore, aiFeedback, aiCompleted }

        // 模拟考试配置
        const EXAM_CHAPTERS = {
            3: { count: 2, scores: [6, 6] },      // 第三章 12分
            4: { count: 2, scores: [12, 13] },     // 第四章 25分
            5: { count: 3, scores: [6, 6, 8] },    // 第五章 20分
            6: { count: 3, scores: [10, 10, 10] }, // 第六章 30分
            8: { count: 2, scores: [6, 7] }        // 第八章 13分
        };
        let examQuestionMaxScores = [];
        let examScores = [];
        let examTotalMax = 0;

        // ========== 初始化 ==========
        function init() {
            loadStats();
            renderChapterList();
            renderWrongList();
            updateStats();
        }

        // ========== 数据持久化 ==========
        function getData() {
            const data = localStorage.getItem('propertyExamData');
            return data ? JSON.parse(data) : {
                wrongQuestions: [],
                starredQuestions: [],
                stats: {},
                todayDate: new Date().toDateString(),
                todayAnswered: 0
            };
        }

        function saveData(data) {
            data.todayDate = new Date().toDateString();
            localStorage.setItem('propertyExamData', JSON.stringify(data));
        }

        function loadStats() {
            const data = getData();
            const today = new Date().toDateString();
            if (data.todayDate !== today) {
                data.todayDate = today;
                data.todayAnswered = 0;
                saveData(data);
            }
        }

        // ========== 统计显示 ==========
        function updateStats() {
            const data = getData();
            const total = questions.length;
            const allStats = data.stats || {};
            let correctCount = 0;
            let totalAnswered = 0;
            Object.values(allStats).forEach(q => {
                if (q.answered) {
                    totalAnswered++;
                    if (q.correct) correctCount++;
                }
            });
            const rate = totalAnswered > 0 ? Math.floor((correctCount / totalAnswered) * 100) : 0;
            const todayAnswered = data.todayAnswered || 0;
            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-correct').textContent = correctCount;
            document.getElementById('stat-today').textContent = todayAnswered;
            document.getElementById('stat-rate').textContent = rate + '%';
        }

        // ========== 章节列表渲染 ==========
        function renderChapterList() {
            const list = document.getElementById('chapter-list');
            const data = getData();
            const stats = data.stats || {};
            let html = '';
            chapters.forEach(ch => {
                const chQuestions = questions.filter(q => q.chapter === ch.id);
                const answered = chQuestions.filter(q => stats[q.id] && stats[q.id].answered).length;
                const total = chQuestions.length;
                const rate = total > 0 ? Math.floor((answered / total) * 100) : 0;
                html += '<li class="chapter-item" onclick="startChapterPractice(\\'' + ch.id + '\\')">'
                    + '<div class="chapter-icon ' + ch.id + '">' + ch.icon + '</div>'
                    + '<div class="chapter-info">'
                    + '<div class="chapter-title">' + ch.name + '</div>'
                    + '<div class="chapter-meta">' + total + '题 · ' + ch.score + ' · 完成' + rate + '%</div>'
                    + '<div class="chapter-progress"><div class="chapter-progress-fill" style="width:' + rate + '%"></div></div>'
                    + '</div>'
                    + '<div class="chapter-arrow">›</div>'
                    + '</li>';
            });
            list.innerHTML = html;
        }

        // ========== 错题列表渲染 ==========
        function renderWrongList() {
            const data = getData();
            const wrongIds = data.wrongQuestions || [];
            const container = document.getElementById('wrong-list-container');
            const practiceAllBtn = document.getElementById('wrong-practice-all-btn');
            if (practiceAllBtn) {
                practiceAllBtn.style.display = wrongIds.length > 1 ? 'block' : 'none';
            }
            if (wrongIds.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">✅</div><div>暂无错题</div><div style="margin-top:8px;font-size:12px;">继续保持！</div></div>';
                return;
            }
            const wrongQuestions = wrongIds.map(id => questions.find(q => q.id === id)).filter(Boolean);
            let html = '<ul class="wrong-list">';
            wrongQuestions.forEach(q => {
                html += '<li class="wrong-item" onclick="startWrongPractice(' + q.id + ')">'
                    + '<div class="wrong-title">' + escHtml(q.question.substring(0, 60)) + (q.question.length > 60 ? '...' : '') + '</div>'
                    + '<div class="wrong-meta"><span>' + q.chapterName + '</span><span>' + q.type + '</span></div>'
                    + '</li>';
            });
            html += '</ul>';
            container.innerHTML = html;
        }

        function escHtml(s) {
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        }

        // ========== 页面导航 ==========
        function showPage(page, navEl) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('page-' + page).classList.add('active');
            if (navEl) {
                navEl.classList.add('active');
            } else {
                // 找到对应的nav item
                var navItems = document.querySelectorAll('.nav-item');
                navItems.forEach(function(n) {
                    if (n.getAttribute('onclick').indexOf("'" + page + "'") > -1) {
                        n.classList.add('active');
                    }
                });
            }
            // 刷新数据
            if (page === 'home') {
                updateStats();
                renderChapterList();
            }
            if (page === 'wrong') {
                renderWrongList();
            }
        }

        // ========== 练习入口 ==========

        // 每日刷题：随机出全部题
        function startDailyPractice() {
            currentMode = 'daily';
            currentQuestions = [...questions].sort(() => Math.random() - 0.5);
            currentQuestionIndex = 0;
            answeredMap.clear();
            openQuestionPage();
        }

        // 章节练习：按顺序出题
        function startChapterPractice(chapterId) {
            currentMode = 'chapter';
            currentQuestions = questions.filter(q => q.chapter === chapterId);
            currentQuestionIndex = 0;
            answeredMap.clear();
            openQuestionPage();
        }

        // 错题练习
        function startWrongPractice(questionId) {
            currentMode = 'wrong';
            const data = getData();
            const wrongIds = data.wrongQuestions || [];
            if (questionId) {
                // 练习单题
                currentQuestions = questions.filter(q => q.id === questionId);
            } else {
                // 练习全部错题
                currentQuestions = wrongIds.map(id => questions.find(q => q.id === id)).filter(Boolean);
            }
            if (currentQuestions.length === 0) {
                showToast('没有错题可练习');
                return;
            }
            currentQuestionIndex = 0;
            answeredMap.clear();
            openQuestionPage();
        }

        // 模拟考试
        function startExamPractice() {
            currentMode = 'exam';
            examQuestionMaxScores = [];
            examScores = [];
            examTotalMax = 0;
            currentQuestions = [];
            answeredMap.clear();

            const chapterKeys = Object.keys(EXAM_CHAPTERS).map(Number).sort((a, b) => a - b);
            chapterKeys.forEach(chNum => {
                const cfg = EXAM_CHAPTERS[chNum];
                const chId = 'ch' + chNum;
                const chQuestions = questions.filter(q => q.chapter === chId);
                const shuffled = [...chQuestions].sort(() => Math.random() - 0.5);
                const selected = shuffled.slice(0, cfg.count);
                selected.forEach((q, i) => {
                    currentQuestions.push(q);
                    examQuestionMaxScores.push(cfg.scores[i]);
                });
            });

            // 全部打乱顺序
            const combined = currentQuestions.map((q, i) => ({ q, maxScore: examQuestionMaxScores[i] }));
            combined.sort(() => Math.random() - 0.5);
            currentQuestions = combined.map(c => c.q);
            examQuestionMaxScores = combined.map(c => c.maxScore);

            examTotalMax = examQuestionMaxScores.reduce((a, b) => a + b, 0);
            currentQuestionIndex = 0;
            openQuestionPage();
        }

        // ========== 答题页面 ==========
        function openQuestionPage() {
            showQuestion();
            document.getElementById('question-page').classList.add('active');
        }

        function closeQuestion() {
            document.getElementById('question-page').classList.remove('active');
            updateStats();
            renderChapterList();
            renderWrongList();
        }

        function showQuestion() {
            const q = currentQuestions[currentQuestionIndex];
            const total = currentQuestions.length;
            const data = getData();

            // 更新进度
            if (currentMode === 'exam') {
                var totalScoreSoFar = 0;
                for (var si = 0; si < examScores.length; si++) totalScoreSoFar += examScores[si];
                document.getElementById('question-progress').textContent = '第' + (currentQuestionIndex + 1) + '题/共' + total + '题 · 总分' + totalScoreSoFar + '/' + examTotalMax;
            } else {
                document.getElementById('question-progress').textContent = (currentQuestionIndex + 1) + '/' + total;
            }

            // 题目类型
            document.getElementById('question-type').textContent = q.type;

            // 考试进度条和本题满分
            var examBar = document.getElementById('exam-progress-bar');
            var examLabel = document.getElementById('exam-score-label');
            if (currentMode === 'exam') {
                examBar.classList.add('show');
                examLabel.classList.add('show');
                var progress = ((currentQuestionIndex + 1) / total) * 100;
                document.getElementById('exam-progress-fill').style.width = progress + '%';
                examLabel.textContent = '本题满分：' + examQuestionMaxScores[currentQuestionIndex] + '分';
            } else {
                examBar.classList.remove('show');
                examLabel.classList.remove('show');
            }

            // 题目内容
            document.getElementById('question-text').textContent = q.question;

            // 背景资料
            var contextEl = document.getElementById('question-context');
            if (q.context) {
                contextEl.style.display = 'block';
                contextEl.textContent = q.context;
            } else {
                contextEl.style.display = 'none';
            }

            // 收藏状态
            isStarred = data.starredQuestions && data.starredQuestions.includes(q.id);
            updateStarBtn();

            // 根据是否已答过设置UI
            var alreadyAnswered = answeredMap.has(q.id);
            if (alreadyAnswered) {
                restoreAnsweredState(q);
            } else {
                resetToUnanswered();
            }

            // 滚到顶部
            document.getElementById('question-content').scrollTop = 0;
        }

        // 恢复已答题状态
        function restoreAnsweredState(q) {
            hasSubmitted = true;
            var info = answeredMap.get(q.id);
            userAnswer = info.userAnswer;

            // 隐藏输入框，显示用户答案
            document.getElementById('user-answer').value = '';
            document.getElementById('input-area').style.display = 'none';
            var displayEl = document.getElementById('user-answer-display');
            displayEl.textContent = userAnswer;
            displayEl.style.display = 'block';

            // 显示参考答案
            document.getElementById('answer-text').textContent = q.answer;
            document.getElementById('answer-section').classList.add('show');

            // 显示AI评分结果
            if (info.aiCompleted) {
                var maxS = info.maxScore;
                var score = info.score;
                var fb = info.aiFeedback || '';
                var rate = maxS > 0 ? score / maxS : 0;
                var isPass = rate >= 0.6;
                document.getElementById('feedback').className = 'feedback show ' + (isPass ? 'correct' : 'wrong');
                document.getElementById('feedback-icon').textContent = isPass ? '✅' : '❌';
                document.getElementById('feedback-text').textContent = 'AI评分：' + score + '/' + maxS + '分' + (fb ? ' · ' + fb : '');
            } else {
                // AI评分还未完成，显示loading
                document.getElementById('feedback').className = 'feedback show';
                document.getElementById('feedback-icon').innerHTML = '<div class="ai-scoring-loading"><div class="spinner"></div><p>AI评分中...</p></div>';
                document.getElementById('feedback-text').textContent = '';
            }

            // 隐藏提交按钮
            document.getElementById('submit-btn').style.display = 'none';

            // 更新导航按钮
            updateNavigationButtons();

            // 考试模式不显示重做按钮
            if (currentMode !== 'exam') {
                document.getElementById('redo-btn').style.display = 'block';
            } else {
                document.getElementById('redo-btn').style.display = 'none';
            }
        }

        // 重置为未答题状态
        function resetToUnanswered() {
            hasSubmitted = false;
            userAnswer = '';

            // 显示输入框
            document.getElementById('input-area').style.display = 'block';
            document.getElementById('user-answer').value = '';
            document.getElementById('user-answer-display').style.display = 'none';

            // 隐藏参考答案和反馈
            document.getElementById('answer-section').classList.remove('show');
            document.getElementById('feedback').classList.remove('show');
            document.getElementById('feedback').className = 'feedback';

            // 显示提交，隐藏导航
            document.getElementById('submit-btn').style.display = 'block';
            document.getElementById('prev-btn').style.display = 'none';
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('redo-btn').style.display = 'none';
        }

        // ========== 提交答案（入口） ==========
        function submitAnswer() {
            if (hasSubmitted) return;

            var q = currentQuestions[currentQuestionIndex];
            var userAns = document.getElementById('user-answer').value.trim();
            if (!userAns) {
                showToast('请先输入答案');
                return;
            }

            hasSubmitted = true;
            userAnswer = userAns;

            if (currentMode === 'exam') {
                submitExamAnswer(q, userAns);
            } else {
                submitNonExamAnswer(q, userAns);
            }
        }

        // ========== 非考试模式提交 ==========
        async function submitNonExamAnswer(q, userAns) {
            var maxScore = 100; // 非考试模式100分制

            // 隐藏输入框，显示用户答案
            document.getElementById('input-area').style.display = 'none';
            var displayEl = document.getElementById('user-answer-display');
            displayEl.textContent = userAns;
            displayEl.style.display = 'block';

            // 隐藏提交按钮
            document.getElementById('submit-btn').style.display = 'none';

            // ★ 立即显示参考答案
            document.getElementById('answer-text').textContent = q.answer;
            document.getElementById('answer-section').classList.add('show');

            // ★ 立即显示AI评分loading
            document.getElementById('feedback').className = 'feedback show';
            document.getElementById('feedback-icon').innerHTML = '<div class="ai-scoring-loading"><div class="spinner"></div><p>AI评分中...</p></div>';
            document.getElementById('feedback-text').textContent = '';

            // ★ 立即显示导航按钮和重做按钮
            updateNavigationButtons();
            document.getElementById('redo-btn').style.display = 'block';

            // 保存答题记录（标记为已答，AI未完成）
            answeredMap.set(q.id, { userAnswer: userAns, score: 0, maxScore: maxScore, aiFeedback: '', aiCompleted: false });

            // 更新统计
            var data = getData();
            if (!data.stats) data.stats = {};
            if (!data.stats[q.id]) data.stats[q.id] = { answered: false, correct: false };
            data.stats[q.id].answered = true;
            if (typeof data.todayAnswered === 'undefined') data.todayAnswered = 0;
            data.todayAnswered++;
            saveData(data);
            updateStats();
            renderChapterList();

            // ★ 异步AI评分
            var score = 0;
            var aiFeedback = '';
            try {
                var result = await aiScoreQuestion(q, userAns, maxScore);
                score = result.score;
                aiFeedback = result.feedback || '';
            } catch (e) {
                console.error('AI评分失败:', e);
                score = 0;
                aiFeedback = 'AI评分失败，请参考标准答案自行评分';
            }

            // 分数钳位
            score = Math.floor(Number(score));
            score = Math.min(score, maxScore);
            score = Math.max(score, 0);

            var scoreRate = maxScore > 0 ? score / maxScore : 0;

            // 更新答题记录（AI已完成）
            answeredMap.set(q.id, { userAnswer: userAns, score: score, maxScore: maxScore, aiFeedback: aiFeedback, aiCompleted: true });

            // 更新统计：正确判断
            var data2 = getData();
            data2.stats[q.id].correct = scoreRate >= 0.6;

            // 得分率<60%自动加错题本
            if (scoreRate < 0.6) {
                if (!data2.wrongQuestions) data2.wrongQuestions = [];
                if (!data2.wrongQuestions.includes(q.id)) {
                    data2.wrongQuestions.push(q.id);
                }
            } else {
                // 得分率>=60%，从错题本移除
                if (data2.wrongQuestions) {
                    var idx = data2.wrongQuestions.indexOf(q.id);
                    if (idx > -1) data2.wrongQuestions.splice(idx, 1);
                }
            }
            saveData(data2);

            // ★ 更新界面上的评分结果
            var isPass = scoreRate >= 0.6;
            document.getElementById('feedback').className = 'feedback show ' + (isPass ? 'correct' : 'wrong');
            document.getElementById('feedback-icon').textContent = isPass ? '✅' : '❌';
            document.getElementById('feedback-text').textContent = 'AI评分：' + score + '/' + maxScore + '分' + (aiFeedback ? ' · ' + aiFeedback : '');

            updateStats();
            renderWrongList();
        }

        // ========== 考试模式提交 ==========
        async function submitExamAnswer(q, userAns) {
            var qMax = examQuestionMaxScores[currentQuestionIndex];

            // 隐藏输入框，显示用户答案
            document.getElementById('input-area').style.display = 'none';
            var displayEl = document.getElementById('user-answer-display');
            displayEl.textContent = userAns;
            displayEl.style.display = 'block';

            // 隐藏提交按钮
            document.getElementById('submit-btn').style.display = 'none';

            // 显示AI评分loading
            document.getElementById('feedback').className = 'feedback show';
            document.getElementById('feedback-icon').innerHTML = '<div class="ai-scoring-loading"><div class="spinner"></div><p>AI评分中...</p></div>';
            document.getElementById('feedback-text').textContent = '';

            // 保存到已答记录
            answeredMap.set(q.id, { userAnswer: userAns, score: 0, maxScore: qMax, aiFeedback: '', aiCompleted: false });

            // 等待AI评分
            var score = 0;
            var aiFeedback = '';
            try {
                var result = await aiScoreQuestion(q, userAns, qMax);
                score = result.score;
                aiFeedback = result.feedback || '';
            } catch (e) {
                console.error('AI评分失败:', e);
                score = 0;
                aiFeedback = 'AI评分失败，请参考标准答案自行评分';
            }

            // 分数钳位
            score = Math.floor(Number(score));
            score = Math.min(score, qMax);
            score = Math.max(score, 0);

            examScores.push(score);

            // 更新已答记录
            answeredMap.set(q.id, { userAnswer: userAns, score: score, maxScore: qMax, aiFeedback: aiFeedback, aiCompleted: true });

            // 保存统计
            var data = getData();
            if (!data.stats) data.stats = {};
            if (!data.stats[q.id]) data.stats[q.id] = { answered: false, correct: false };
            data.stats[q.id].answered = true;
            var scoreRate = qMax > 0 ? score / qMax : 0;
            data.stats[q.id].correct = scoreRate >= 0.6;
            if (typeof data.todayAnswered === 'undefined') data.todayAnswered = 0;
            data.todayAnswered++;

            // 得分率<60%自动加错题本
            if (scoreRate < 0.6) {
                if (!data.wrongQuestions) data.wrongQuestions = [];
                if (!data.wrongQuestions.includes(q.id)) {
                    data.wrongQuestions.push(q.id);
                }
            }
            saveData(data);

            // 显示参考答案
            document.getElementById('answer-text').textContent = q.answer;
            document.getElementById('answer-section').classList.add('show');

            // 显示评分结果
            var isPass = scoreRate >= 0.6;
            document.getElementById('feedback').className = 'feedback show ' + (isPass ? 'correct' : 'wrong');
            document.getElementById('feedback-icon').textContent = isPass ? '✅' : '❌';
            document.getElementById('feedback-text').textContent = 'AI评分：' + score + '/' + qMax + '分' + (aiFeedback ? ' · ' + aiFeedback : '');

            // 更新导航（考试模式：不显示上一题和重做）
            updateNavigationButtons();

            // 更新进度显示
            var totalScoreSoFar = 0;
            for (var si = 0; si < examScores.length; si++) totalScoreSoFar += examScores[si];
            var totalQ = currentQuestions.length;
            document.getElementById('question-progress').textContent = '第' + (currentQuestionIndex + 1) + '题/共' + totalQ + '题 · 总分' + totalScoreSoFar + '/' + examTotalMax;

            updateStats();
            renderChapterList();
            renderWrongList();
        }

        // ========== AI评分 ==========
        async function aiScoreQuestion(q, userAns, maxScore) {
            var COZE_API = 'https://api.coze.cn/v3/chat';
            var COZE_TOKEN = 'pat_0mIoNSZLbFzfzxKH7B73ojGULZQefWyFiIbEeSmYxlmhmBTzXsiiebvcKktbF07c';
            var COZE_BOT_ID = '7639707793037508642';

            var prompt = '你是一位物业初级考试评分老师。请根据以下信息对考生的答案进行评分。\\n\\n'
                + '【题目】' + q.question + '\\n'
                + (q.context ? '【背景资料】' + q.context + '\\n' : '')
                + '【参考答案】' + q.answer + '\\n'
                + '【考生答案】' + userAns + '\\n'
                + '【本题满分】' + maxScore + '分\\n\\n'
                + '评分要求：\\n'
                + '1. 严格按照' + maxScore + '分制评分，给出0到' + maxScore + '之间的整数分数\\n'
                + '2. 对比参考答案的要点，按得分点评分\\n'
                + '3. 如果考生答案涵盖大部分要点，给予较高分数；遗漏较多则扣分\\n'
                + '4. 简要说明扣分原因\\n\\n'
                + '请严格按照以下JSON格式回复（不要有其他内容）：\\n'
                + '{"score": 分数, "feedback": "简要评语"}';

            var response = await fetch(COZE_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + COZE_TOKEN
                },
                body: JSON.stringify({
                    bot_id: COZE_BOT_ID,
                    user_id: 'exam_user_' + Date.now(),
                    stream: false,
                    auto_save_history: false,
                    additional_messages: [{
                        role: 'user',
                        content: prompt,
                        content_type: 'text'
                    }]
                })
            });

            if (!response.ok) {
                throw new Error('API请求失败: ' + response.status);
            }

            var result = await response.json();

            // 从Coze API响应中提取内容
            var content = '';
            if (result.data && result.data.length > 0) {
                for (var i = 0; i < result.data.length; i++) {
                    var item = result.data[i];
                    if (item.type === 'answer' || item.role === 'assistant') {
                        content += item.content || '';
                    }
                }
            }
            if (!content && result.messages) {
                for (var j = 0; j < result.messages.length; j++) {
                    var msg = result.messages[j];
                    if (msg.role === 'assistant' && msg.type === 'answer') {
                        content += msg.content || '';
                    }
                }
            }

            // 尝试解析JSON
            try {
                var cleaned = content.replace(/```json\\s*/g, '').replace(/```\\s*/g, '').trim();
                var parsed = JSON.parse(cleaned);
                return {
                    score: parseInt(parsed.score) || 0,
                    feedback: parsed.feedback || ''
                };
            } catch (parseErr) {
                var scoreMatch = content.match(/"score"\\s*:\\s*(\\d+)/);
                var feedbackMatch = content.match(/"feedback"\\s*:\\s*"([^"]*)"/);
                if (scoreMatch) {
                    return {
                        score: parseInt(scoreMatch[1]) || 0,
                        feedback: feedbackMatch ? feedbackMatch[1] : ''
                    };
                }
                throw new Error('无法解析AI评分结果: ' + content);
            }
        }

        // ========== 导航按钮管理 ==========
        function updateNavigationButtons() {
            var prevBtn = document.getElementById('prev-btn');
            var nextBtn = document.getElementById('next-btn');
            var redoBtn = document.getElementById('redo-btn');

            // 考试模式：不显示上一题和重做按钮
            if (currentMode === 'exam') {
                prevBtn.style.display = 'none';
                redoBtn.style.display = 'none';
            } else {
                prevBtn.style.display = currentQuestionIndex > 0 ? 'block' : 'none';
                redoBtn.style.display = 'block';
            }

            // 下一题按钮文字
            var isLast = currentQuestionIndex >= currentQuestions.length - 1;
            if (isLast) {
                nextBtn.textContent = currentMode === 'exam' ? '交卷' : '完成练习';
            } else {
                nextBtn.textContent = '下一题';
            }
            nextBtn.style.display = 'block';
        }

        // 上一题
        function prevQuestion() {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                showQuestion();
            }
        }

        // 下一题
        function nextQuestion() {
            if (currentQuestionIndex >= currentQuestions.length - 1) {
                // 最后一题
                if (currentMode === 'exam') {
                    showExamTranscript();
                } else {
                    closeQuestion();
                    showToast('恭喜完成练习！');
                }
                return;
            }
            currentQuestionIndex++;
            showQuestion();
        }

        // 重做当前题目
        function redoCurrentQuestion() {
            var q = currentQuestions[currentQuestionIndex];
            // 从已答记录中移除
            answeredMap.delete(q.id);
            // 重置状态
            hasSubmitted = false;
            userAnswer = '';
            // 重置UI
            resetToUnanswered();
            showToast('已重置，请重新作答');
        }

        // ========== 考试成绩单 ==========
        function showExamTranscript() {
            var totalScore = 0;
            for (var i = 0; i < examScores.length; i++) totalScore += examScores[i];
            var scoreRate = examTotalMax > 0 ? Math.floor((totalScore / examTotalMax) * 100) : 0;

            // 关闭答题页面
            document.getElementById('question-page').classList.remove('active');

            // 设置总分
            document.getElementById('transcript-total').innerHTML = totalScore + '<small>/' + examTotalMax + '</small>';
            document.getElementById('transcript-rate').textContent = scoreRate + '%';

            // 按章节遍历生成成绩单
            var html = '';
            var qIndex = 0;
            var chapterKeys = Object.keys(EXAM_CHAPTERS).map(Number).sort(function(a, b) { return a - b; });
            chapterKeys.forEach(function(chNum) {
                var cfg = EXAM_CHAPTERS[chNum];
                var chInfo = chapters.find(function(c) { return c.id === 'ch' + chNum; });
                html += '<div class="transcript-chapter">';
                html += '<div class="transcript-chapter-title">' + (chInfo ? chInfo.name : '第' + chNum + '章') + '</div>';
                for (var i = 0; i < cfg.count; i++) {
                    if (qIndex >= examScores.length) break;
                    var score = examScores[qIndex];
                    var maxS = examQuestionMaxScores[qIndex];
                    var rate = maxS > 0 ? score / maxS : 0;
                    var isPass = rate >= 0.6;
                    var q = currentQuestions[qIndex];
                    html += '<div class="transcript-item">';
                    html += '<div class="transcript-item-index ' + (isPass ? 'pass' : 'fail') + '">' + (qIndex + 1) + '</div>';
                    html += '<div class="transcript-item-q">' + escHtml(q.question.substring(0, 50)) + (q.question.length > 50 ? '...' : '') + '</div>';
                    html += '<div class="transcript-item-score ' + (isPass ? 'pass' : 'fail') + '">' + score + '</div>';
                    html += '<div class="transcript-item-max">/' + maxS + '</div>';
                    html += '</div>';
                    qIndex++;
                }
                html += '</div>';
            });
            document.getElementById('transcript-body').innerHTML = html;

            // 统计及格/不及格题数
            var passCount = 0, failCount = 0;
            for (var i = 0; i < examScores.length; i++) {
                var maxS = examQuestionMaxScores[i];
                var rate = maxS > 0 ? examScores[i] / maxS : 0;
                if (rate >= 0.6) passCount++;
                else failCount++;
            }
            document.getElementById('transcript-pass-count').textContent = passCount;
            document.getElementById('transcript-fail-count').textContent = failCount;

            document.getElementById('exam-transcript').classList.add('show');
        }

        function closeTranscript() {
            document.getElementById('exam-transcript').classList.remove('show');
            showPage('home');
        }

        // ========== 收藏 ==========
        function toggleStar() {
            var q = currentQuestions[currentQuestionIndex];
            var data = getData();
            if (!data.starredQuestions) data.starredQuestions = [];
            var index = data.starredQuestions.indexOf(q.id);
            if (index > -1) {
                data.starredQuestions.splice(index, 1);
                isStarred = false;
            } else {
                data.starredQuestions.push(q.id);
                isStarred = true;
            }
            saveData(data);
            updateStarBtn();
            showToast(isStarred ? '已收藏' : '已取消收藏');
        }

        function updateStarBtn() {
            var btn = document.getElementById('star-btn');
            btn.textContent = isStarred ? '★' : '☆';
            btn.className = 'star-btn' + (isStarred ? ' starred' : '');
        }

        // ========== Toast ==========
        function showToast(msg) {
            var toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(function() { toast.classList.remove('show'); }, 1500);
        }

        // ========== 初始化 ==========
        init();
    </script>
</body>
</html>'''

with open('/home/user/property-quiz/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! File written successfully.")
