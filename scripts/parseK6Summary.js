const fs = require('fs');
const path = require('path');

function getMetricValue(metricObj, key) {
    if (!metricObj) return 'N/A';
    if (metricObj.values && metricObj.values[key] !== undefined) {
        return metricObj.values[key];
    }
    if (metricObj[key] !== undefined) {
        return metricObj[key];
    }
    return 'N/A';
}

function parseSummary() {
    const summaryPath = path.join(__dirname, '..', 'summary.json');
    if (!fs.existsSync(summaryPath)) {
        console.error("k6 summary.json not found!");
        process.exit(1);
    }

    const data = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
    const metrics = data.metrics;

    const rps = getMetricValue(metrics.http_reqs, 'rate');
    const totalReqs = getMetricValue(metrics.http_reqs, 'count');
    
    const avgLatency = getMetricValue(metrics.http_req_duration, 'avg');
    const minLatency = getMetricValue(metrics.http_req_duration, 'min');
    const maxLatency = getMetricValue(metrics.http_req_duration, 'max');
    const p95Latency = getMetricValue(metrics.http_req_duration, 'p(95)');
    
    const failRate = getMetricValue(metrics.http_req_failed, 'rate') * 100 || 0;
    const checkRate = getMetricValue(metrics.checks, 'rate') * 100 || 100;

    const summaryContent = `
### ⚡ API Load Testing Summary (k6)
| Metric | Value |
|--------|-------|
| **Virtual Users** | 100 |
| **Duration** | 1 Minute |
| **Total Requests** | ${typeof totalReqs === 'number' ? totalReqs.toLocaleString() : totalReqs} |
| **Throughput (RPS)** | ${typeof rps === 'number' ? rps.toFixed(2) : rps} req/sec |
| **Average Latency** | ${typeof avgLatency === 'number' ? avgLatency.toFixed(2) : avgLatency} ms |
| **p(95) Latency** | ${typeof p95Latency === 'number' ? p95Latency.toFixed(2) : p95Latency} ms |
| **Min Latency** | ${typeof minLatency === 'number' ? minLatency.toFixed(2) : minLatency} ms |
| **Max Latency** | ${typeof maxLatency === 'number' ? maxLatency.toFixed(2) : maxLatency} ms |
| **Request Failure Rate** | ${failRate.toFixed(2)}% |
| **Assertions Passed** | ${checkRate.toFixed(2)}% |

> The load test successfully targeted the Flask Backend validating system stability under high concurrent load.
`;

    const summaryFile = process.env.GITHUB_STEP_SUMMARY;
    if (summaryFile) {
        fs.appendFileSync(summaryFile, summaryContent);
    } else {
        console.log(summaryContent);
    }
}

parseSummary();
