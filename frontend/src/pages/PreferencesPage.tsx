import React, { useState, useEffect } from 'react';
import '../styles/PreferencesPage.css'; // CSS 파일을 import 합니다.

// 카테고리 데이터를 위한 타입 정의
interface GroupedCategories {
  categories: string[];
}

// 사용자 설정을 위한 타입 정의
interface UserPreferences {
  name?: string;
  email: string;
  chat_id?: string;
  time_slots?: string[];
  categories?: string[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PreferencesPage() {
  const [nickname, setNickname] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [chatId, setChatId] = useState<string>('');
  const [selectedTimeSlots, setSelectedTimeSlots] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isNicknameReadOnly, setIsNicknameReadOnly] = useState<boolean>(false);
  const [groupedSources, setGroupedSources] = useState<GroupedCategories>({}); // 서버에서 받아올 카테고리 데이터


  useEffect(() => {

    document.title = '구독정보 업데이트';

    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const emailParam = urlParams.get('email'); // 이메일 파라미터도 있으니 혹시 몰라 추가

    const loadPreferences = async () => {
      if (token) {
        try {
          const res = await fetch(`${API_BASE_URL}/get-preferences-by-token?token=${encodeURIComponent(token)}`);
          const result: UserPreferences & { error?: string } = await res.json();

          if (result.error) {
            setStatusMessage('❌ 인증에 실패했습니다.');
            return;
          }

          setNickname(result.name || '');
          setEmail(result.email || '');
          setChatId(result.chat_id || '');
          setSelectedTimeSlots(result.time_slots || []);
          setSelectedCategories(result.categories || []);

          if (result.chat_id) {
            setIsNicknameReadOnly(true); // chat_id가 있으면 닉네임 수정 불가
          }

          // 인사말 업데이트
          document.getElementById('user-greeting')!.innerText = `반가워요 ${result.name || ""}님!\n뉴스레터를 받을 시간을 선택하세요. 📌`;

          // 카테고리 데이터도 여기서 함께 가져온다고 가정
          // 실제 API는 /get-categories와 동일할 수 있음
          const categoriesRes = await fetch(`${API_BASE_URL}/get-categories`); // 예시: 카테고리 API
          const categoriesData = await categoriesRes.json();
          setGroupedSources(categoriesData);


        } catch (error) {
          console.error('설정 불러오기 실패:', error);
          setStatusMessage('오류가 발생했습니다.');
        }
      } else if (emailParam) {
        // 토큰 없이 이메일만 있는 경우 처리 (필요하다면)
        setEmail(emailParam);
        // 이 경우, preferences 데이터를 불러오는 다른 API가 필요할 수 있습니다.
        // 여기서는 기본값으로 초기화합니다.
        const categoriesRes = await fetch(`${API_BASE_URL}/get-categories`); // 예시: 카테고리 API
          const categoriesData = await categoriesRes.json();
          setGroupedSources(categoriesData);
      }
    };

    loadPreferences();
  }, []); // 컴포넌트 마운트 시 한 번만 실행

  const handleTimeSlotChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSelectedTimeSlots(prev =>
      e.target.checked ? [...prev, value] : prev.filter(time => time !== value)
    );
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSelectedCategories(prev =>
      e.target.checked ? [...prev, value] : prev.filter(category => category !== value)
    );
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const modifiedAt = new Date().toISOString();

    try {
      const res = await fetch(`${API_BASE_URL}/update-preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          chat_id: chatId,
          name: nickname,
          time_slots: selectedTimeSlots,
          categories: selectedCategories,
          modified_at: modifiedAt,
        }),
      });
      const result: { message?: string; error?: string } = await res.json();

      setStatusMessage(result.message || result.error || '저장 실패!');

      setTimeout(() => {
        setStatusMessage('');
      }, 1000);
    } catch (error) {
      console.error('설정 저장 실패:', error);
      setStatusMessage('오류가 발생했습니다.');
    }
  };

  return (
    <div className="card">
      <h2 id="user-greeting">⏰ 뉴스레터 수신 시간대 선택</h2>
      <p>원하는 시간을 선택하면<br />그 시간에만 뉴스레터를 받아볼 수 있어요.</p>

      {chatId && ( // chat_id가 있을 경우에만 렌더링
        <div style={{ background: '#f4f8ff', border: '1px solid #cce1ff', borderRadius: '8px', padding: '16px', margin: '24px 0' }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, fontSize: '15px' }}>
            📬 더 풍부한 뉴스 요약을 <strong>이메일로 받아보고 싶다면?</strong>
          </p>
          <div style={{ textAlign: 'center' }}>
            <a target="_blank" href="/news-bot?subscribe"
              style={{ display: 'inline-block', background: '#4a90e2', color: 'white', padding: '8px 20px',
                       fontWeight: 500, borderRadius: '6px', textDecoration: 'none', fontSize: '14px' }}>
              📧 이메일로 구독하기
            </a>
          </div>
        </div>
      )}

      <div className="section">
        <label className="section-label">🏷️ 닉네임</label>
        <div className="form-group">
          <input
            type="text"
            id="nickname"
            name="nickname"
            placeholder="닉네임을 입력하세요"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            readOnly={isNicknameReadOnly} // readOnly 속성 적용
          />
        </div>
      </div>

      {/* 📰 뉴스 카테고리 선택 */}
      <div className="section">
        <label className="section-label">🗞️ 관심 카테고리</label>
        {Object.entries(groupedSources).map(([source, categories]) => (
          <div className="category-block" key={source}>
            <div className="category-header">{source}</div>
            <div className="toggle-grid">
              {categories.map(category => (
                <label className="toggle-item" key={`${source}::${category}`}>
                  <input
                    type="checkbox"
                    name="categories"
                    value={`${source}::${category}`}
                    checked={selectedCategories.includes(`${source}::${category}`)}
                    onChange={handleCategoryChange}
                  />
                  <span>{category}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="section">
        <label className="section-label">⏰ 수신 시간대</label>
        <form id="timeForm" onSubmit={handleSubmit}>
          <div className="time-options">
            {[
              { value: '07:30', label: '오전 7:30 (아침 뉴스)' },
              { value: '11:30', label: '오전 11:30 (오전 브리핑)' },
              { value: '15:30', label: '오후 3:30 (시장 동향)' },
              { value: '17:50', label: '오후 5:50 (퇴근길 요약)' },
              { value: '21:30', label: '오후 9:30 (하루 정리)' },
            ].map(timeOption => (
              <label className="time-card" key={timeOption.value}>
                <input
                  type="checkbox"
                  name="time"
                  value={timeOption.value}
                  checked={selectedTimeSlots.includes(timeOption.value)}
                  onChange={handleTimeSlotChange}
                />
                <span>{timeOption.label}</span>
              </label>
            ))}
          </div>

          {/* Hidden input은 React 상태로 관리되므로 별도로 렌더링할 필요 없음 */}
          <button type="submit">저장하기</button>
        </form>
      </div>

      <div id="status">{statusMessage}</div>
    </div>
  );
}

export default PreferencesPage;