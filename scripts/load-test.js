import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 100,
    duration: '1m',
    thresholds: {
        http_req_failed: ['rate<0.05'], // http errors should be less than 5%
        http_req_duration: ['p(95)<1500'], // 95% of requests should be below 1500ms
    },
};

export default function () {
    const url = __ENV.BACKEND_URL || 'https://nutrimeal-backend-qjqa.onrender.com/api/health';
    
    const res = http.get(url);
    
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
    
    // Tiny sleep to simulate real user pacing and prevent overwhelming free tier completely instantly
    sleep(0.5);
}
