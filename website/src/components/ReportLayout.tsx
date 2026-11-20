import { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { Link, NavLink, useLocation } from 'react-router';
import { applicationUrl } from '../config';
import { reportRoutes } from '../reportRoutes';

export function ReportLayout({ children }: { children: ReactNode }) {
  const location = useLocation();
  const previousLocation = useRef(location);
  const main = useRef<HTMLElement>(null);
  const [menuLocation, setMenuLocation] = useState<string>();
  const menuOpen = menuLocation === location.key;

  useEffect(() => {
    const previous = previousLocation.current;
    previousLocation.current = location;
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (target) {
      target.focus();
      target.scrollIntoView();
    } else if (previous !== location) {
      main.current?.focus({ preventScroll: true });
      window.scrollTo(0, 0);
    }
  }, [location]);

  return (
    <>
      <a className="skip-link" href="#report-main">Skip to report content</a>
      <header className="site-header">
        <div className="site-width header-inner">
          <Link className="wordmark" to="/">
            Hanoi Water Watch <span>CITP Task 3</span>
          </Link>
          <div className="launch">
            {applicationUrl ? (
              <a className="launch-button" href={applicationUrl}>Explore Hanoi WaterWatch</a>
            ) : (
              <>
                <button className="launch-button" disabled aria-describedby="launch-status">Explore Hanoi WaterWatch</button>
                <span id="launch-status">Application link pending</span>
              </>
            )}
          </div>
        </div>
      </header>
      <div className="site-width report-layout">
        <aside className="contents">
          <p className="contents-label">Report contents</p>
          <button className="contents-toggle" type="button" aria-expanded={menuOpen} aria-controls="report-navigation"
            onClick={() => setMenuLocation(menuOpen ? undefined : location.key)}>
            {menuOpen ? 'Hide report contents' : 'Show report contents'}
          </button>
          <nav aria-label="Report contents" id="report-navigation" className={menuOpen ? 'contents-nav open' : 'contents-nav'}>
            <ol>
              {reportRoutes.map(({ path, section }) => (
                <li key={path}>
                  <NavLink to={path} end onClick={() => setMenuLocation(undefined)}>{section.label}</NavLink>
                </li>
              ))}
            </ol>
            <p className="contents-label contents-subhead">Interactive prototype</p>
            <ol>
              <li><NavLink to="/simulator" end onClick={() => setMenuLocation(undefined)}>Sensor simulator</NavLink></li>
              <li><NavLink to="/station" end onClick={() => setMenuLocation(undefined)}>3D station</NavLink></li>
            </ol>
          </nav>
        </aside>
        <main id="report-main" tabIndex={-1} ref={main}>{children}</main>
      </div>
      <footer className="site-footer">
        <div className="site-width footer-inner">
          <span>CITP · Task 3 project report</span>
          <nav aria-label="Report resources">
            <Link to="/pages/references">References</Link>
            <Link to="/pages/appendices">Supporting documents</Link>
          </nav>
        </div>
      </footer>
    </>
  );
}
