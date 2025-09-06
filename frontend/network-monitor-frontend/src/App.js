import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Overview from './pages/Overview';
import './index.css';

function App() {
  return (
    <Router basename="">
      <Layout>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/overview" element={<Overview />} />
          {/* Additional routes will be added tomorrow */}
          <Route path="*" element={
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <h2>Page Coming Soon</h2>
              <p>This section will be implemented in the next phases.</p>
            </div>
          } />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

// import React from 'react';
// import { BrowserRouter, Routes, Route } from 'react-router-dom';

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<h1>Root Page</h1>} />
//         <Route path="/test" element={<h1>Test Page</h1>} />
//         <Route path="*" element={<h1>Not Found</h1>} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;
