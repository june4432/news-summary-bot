import React from 'react';
import '../styles/AuthErrorPage.css'; // 공통 CSS 파일을 사용할 수 있습니다.

function AuthErrorPage() {
  return (
    <div className="error-page-container">
      <div className="emoji">⛔</div>
      <h1>유효하지 않거나 만료된 링크입니다.</h1>
      <p>인증 링크가 잘못되었습니다.<br />최근 발송된 뉴스레터의 <br />설정 버튼을 다시 눌러주세요.</p>
    </div>
  );
}

export default AuthErrorPage;