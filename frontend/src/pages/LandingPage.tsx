import React, { useState, useEffect } from 'react';
import '../styles/LandingPage.css'; // CSS 파일을 import 합니다.
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"; // 라우터 임포트 확인

interface Category {
  [source: string]: string[]; // 카테고리 데이터의 정확한 타입 정의
}

// API 기본 URL 설정 (환경 변수 사용)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function LandingPage() { // 컴포넌트 이름을 LandingPage로 변경
  const [activeTab, setActiveTab] = useState('subscribe');
  const [categories, setCategories] = useState<Category>({}); // 타입 Category로 지정
  const [resultMessage, setResultMessage] = useState('');
  const [resultOpacity, setResultOpacity] = useState(0);


  useEffect(() => {

    document.title = 'AI 뉴스레터를 구독하세요!';
    // URL 파라미터에 따라 탭 활성화
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    if (tabParam === 'subscribe' || tabParam === 'unsubscribe') {
      setActiveTab(tabParam);
    }

    // 카테고리 데이터 가져오기
    fetch(`${API_BASE_URL}/get-categories`)
      .then(res => res.json())
      .then(data => {
        setCategories(data);
      })
      .catch(err => console.error('카테고리 가져오기 실패:', err));
  }, []);

  const switchTab = (tab: string) => {
    setActiveTab(tab);
    setResultMessage(''); // 탭 변경 시 메시지 초기화
    setResultOpacity(0);
  };

  const submitForm = async (event: React.FormEvent, endpoint: string) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const formData = new FormData(form);
    const data: { [key: string]: any } = Object.fromEntries(formData);

    const selectedTimeSlots = Array.from(
      form.querySelectorAll<HTMLInputElement>('input[name="time_slots"]:checked')
    ).map(cb => cb.value);
    data.time_slots = selectedTimeSlots;

    const selectedCategories = Array.from(
      form.querySelectorAll<HTMLInputElement>('input[name="categories"]:checked')
    ).map(cb => cb.value);
    data.categories = selectedCategories;

    // 현재 시간 추가
    const nowIso = new Date().toISOString();
    if (endpoint === '/subscribe') {
      data.subscribe_at = nowIso;
    } else if (endpoint === '/unsubscribe') {
      data.unsubscribe_at = nowIso;
    }

    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const resData = await res.json();
      setResultMessage(resData.message || resData.error || '응답 없음');
      setResultOpacity(1);
      form.reset(); // 폼 초기화

      // 폼 초기화 후 체크박스 상태도 초기화 (시간대는 기본값으로 체크)
      form.querySelectorAll<HTMLInputElement>('input[name="time_slots"]').forEach(cb => {
        if (["07:30", "11:30", "15:30", "17:50", "21:30"].includes(cb.value)) {
          cb.checked = true;
        } else {
          cb.checked = false;
        }
      });
      form.querySelectorAll<HTMLInputElement>('input[name="categories"]').forEach(cb => cb.checked = false);


      setTimeout(() => {
        setResultOpacity(0);
        setResultMessage('');
      }, 1500);
    } catch (err) {
      setResultMessage('오류가 발생했어요.');
      setResultOpacity(1);
      setTimeout(() => {
        setResultOpacity(0);
        setResultMessage('');
      }, 3000);
      console.error(err);
    }
  };

  return (
    <div className="card">
      <h1>📨 뉴스레터 구독 서비스</h1>
      <p>AI가 요약한 테마별 참조 기사를 보내드릴거에요.<br /><strong>지금 구독</strong>해보세요. 📌</p>
      <div style={{ marginTop: '20px', fontSize: '13px', color: '#888', textAlign: 'center' }}>
        <strong style={{ color: '#aaa' }}>발송 시간 🚀</strong><br />
        오전 7시 30분 / 오전 11시 30분 / 오후 3시 30분<br />
        오후 5시 50분 / 오후 9시 30분
      </div>
      <div className="tabs">
        <div className={`tab ${activeTab === 'subscribe' ? 'active' : ''}`} onClick={() => switchTab('subscribe')}>
          구독 신청
        </div>
        <div className={`tab ${activeTab === 'unsubscribe' ? 'active' : ''}`} onClick={() => switchTab('unsubscribe')}>
          구독 해제
        </div>
      </div>

      <div id="subscribe" className={`form-section ${activeTab === 'subscribe' ? 'active' : ''}`}>
        <form onSubmit={e => submitForm(e, '/subscribe')}>
          <label className="section-label">🏷️ 닉네임</label> {/* 라벨 추가 */}
          <input type="text" placeholder="닉네임을 입력하세요" name="name" required /><br />
          <label className="section-label">📬 이메일 주소</label> {/* 라벨 추가 */}
          <input type="email" placeholder="이메일 주소를 입력하세요" name="email" required /><br />

          {/* 🗞️ 관심 카테고리 섹션 */}
          <div className="section"> {/* section 클래스 추가 */}
            <label className="section-label">🗞️ 관심 뉴스와 카테고리</label>
            <div id="category-container">
              {Object.entries(categories).map(([source, cats]) => (
                <div key={source} className="category-block"> {/* category-block 클래스 추가 */}
                  <div className="category-header">{source}</div> {/* category-header 클래스 추가 */}
                  <div className="toggle-grid"> {/* toggle-grid 클래스 추가 */}
                    {cats.map(category => (
                      <label className="toggle-item" key={`${source}-${category}`}> {/* toggle-item 클래스 추가 */}
                        <input type="checkbox" name="categories" value={`${source}:::${category}`} />
                        <span>{category}</span> {/* 텍스트를 span으로 감싸기 */}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ✅ 수신 시간대 섹션 */}
          <div className="section"> {/* section 클래스 추가 */}
            <label className="section-label">⏰ 수신 시간대</label>
            <div className="time-options">
              <label className="toggle-option">
                <input type="checkbox" name="time_slots" value="07:30" defaultChecked />오전 7:30
              </label>
              <label className="toggle-option">
                <input type="checkbox" name="time_slots" value="11:30" defaultChecked />오전 11:30
              </label>
              <label className="toggle-option">
                <input type="checkbox" name="time_slots" value="15:30" defaultChecked />오후 3:30
              </label>
              <label className="toggle-option">
                <input type="checkbox" name="time_slots" value="17:50" defaultChecked />오후 5:50
              </label>
              <label className="toggle-option">
                <input type="checkbox" name="time_slots" value="21:30" defaultChecked />오후 9:30
              </label>
              {/* <label className="toggle-option empty"></label> 이 항목은 필요 없으므로 제거하는 것이 좋습니다. */}
            </div>
          </div>
          <br />
          <button type="submit">구독 신청하기</button>
        </form>
      </div>

      <div id="unsubscribe" className={`form-section ${activeTab === 'unsubscribe' ? 'active' : ''}`}>
        <form onSubmit={e => submitForm(e, '/unsubscribe')}>
          <label className="section-label">📬 이메일 주소</label>
          <input type="email" placeholder="이메일 주소를 입력하세요" name="email" required /><br />
          <button type="submit" style={{ background: '#d93025' }}>구독 해제하기</button>
        </form>
      </div>
      <p id="result" style={{ opacity: resultOpacity }}>{resultMessage}</p>
    </div>
  );
}

export default LandingPage; // 컴포넌트 이름 내보내기