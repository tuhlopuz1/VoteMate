import React, { useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import './styles/swagger.css';
import 'swagger-ui-dist/swagger-ui.css';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
const SwaggerUIPage = () => {
  const swaggerRef = useRef(null);
  const scriptRef = useRef(null);
  const navigate = useNavigate();


  useEffect(() => {
    scriptRef.current = document.createElement('script');
    scriptRef.current.src = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js';
    scriptRef.current.onload = () => {
      // @ts-ignore
      const ui = window.SwaggerUIBundle({
        url: 'https://api.vote.vickz.ru/openapi.json',
        dom_id: '#swagger-ui',
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
        presets: [
          window.SwaggerUIBundle.presets.apis,
          window.SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
      });
      swaggerRef.current = ui;
    };

    document.body.appendChild(scriptRef.current);

    return () => {
      // Удалить содержимое swagger UI
      const el = document.getElementById('swagger-ui');
      if (el) el.innerHTML = '';

      // Удалить скрипт, если нужно
      if (scriptRef.current) {
        document.body.removeChild(scriptRef.current);
      }

      // Удалить ссылки на UI
      swaggerRef.current = null;
    };
  }, []);

  return (
    <div className="main-layout">
      <Sidebar />
              <button className="back-to-home-button" onClick={() => window.location.href = '/#/settings'}>
                <FiArrowLeft size={30} />
              </button>
      <div className="swagger-area">
        <div id="swagger-ui"></div>
      </div>
    </div>
  );
};

export default SwaggerUIPage;
