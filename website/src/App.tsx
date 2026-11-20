import { useEffect } from 'react';
import { Link, Route, Routes } from 'react-router';
import { DemoWorkspace } from './components/DemoWorkspace';
import { ReportLayout } from './components/ReportLayout';
import { ReportPage } from './components/ReportPage';
import { reportRoutes } from './reportRoutes';

function MissingPage() {
  useEffect(() => { document.title = 'Report page unavailable | Hanoi Water Watch'; }, []);
  return (
    <article className="page-intro">
      <h1>Report page unavailable</h1>
      <p>Choose a section from Report contents or <Link to="/">return to the overview</Link>.</p>
    </article>
  );
}

export function App() {
  return (
    <ReportLayout>
      <Routes>
        {reportRoutes.map(({ path }, index) => (
          <Route key={path} path={path} element={<ReportPage index={index} />} />
        ))}
        <Route element={<DemoWorkspace />}>
          <Route path="/simulator" element={null} />
          <Route path="/station" element={null} />
        </Route>
        <Route path="*" element={<MissingPage />} />
      </Routes>
    </ReportLayout>
  );
}
