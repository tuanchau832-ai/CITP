import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router';

const demos = {
  '/simulator': {
    title: 'Sensor simulator',
    summary: 'Change the simulated pH, dissolved oxygen, turbidity and temperature readings of the virtual ESP32 sensor station.',
    frameTitle: 'Interactive ESP32 simulator for the virtual sensor station',
  },
  '/station': {
    title: '3D station',
    summary: 'Explore the river station in 3D. While linked, it shows the readings and limits set in the simulator.',
    frameTitle: 'Interactive 3D model of the water monitoring station',
  },
} as const;

type DemoPath = keyof typeof demos;

const simulatorSrc = '/embed/simulator/Simulation.html';
const stationSrc = '/embed/station/index.html';

/**
 * Hosts the simulator and the 3D station as two pages of the report. This component is a pathless
 * layout route, so it stays mounted when the reader switches between /simulator and /station. Both
 * iframes therefore keep running: the simulator keeps publishing its sensor state and the station
 * keeps showing it, so parameters changed on one page are already applied on the other.
 *
 * Both iframes are sandboxed with opaque origins, so messages are matched on the sending window,
 * never on the origin. The inactive iframe is made transparent rather than hidden, because browsers
 * pause animation in hidden cross-origin frames.
 */
export function DemoWorkspace() {
  const { pathname } = useLocation();
  const active: DemoPath = pathname === '/station' ? '/station' : '/simulator';
  const demo = demos[active];
  const simulator = useRef<HTMLIFrameElement>(null);
  const station = useRef<HTMLIFrameElement>(null);
  const [linked, setLinked] = useState(true);

  useEffect(() => {
    document.title = `${demo.title} | Hanoi Water Watch`;
  }, [demo.title]);

  useEffect(() => {
    if (!linked) {
      station.current?.contentWindow?.postMessage({ type: 'station-unlink' }, '*');
      return;
    }
    function forward(event: MessageEvent) {
      if (event.source !== simulator.current?.contentWindow) return;
      const data: unknown = event.data;
      if (typeof data !== 'object' || data === null || (data as { type?: unknown }).type !== 'station-state') return;
      station.current?.contentWindow?.postMessage(data, '*');
    }
    window.addEventListener('message', forward);
    return () => window.removeEventListener('message', forward);
  }, [linked]);

  const other: DemoPath = active === '/simulator' ? '/station' : '/simulator';

  return (
    <article>
      <header className="page-intro">
        <p className="draft-status">DRAFT — content pending verification</p>
        <h1>{demo.title}</h1>
        <p className="intro-copy">{demo.summary}</p>
      </header>
      <section className="report-topic" aria-label="Linked prototype pages">
        <div className="demo-toolbar">
          <nav aria-label="Prototype pages" className="demo-tabs">
            <NavLink to="/simulator">Simulator</NavLink>
            <NavLink to="/station">3D station</NavLink>
          </nav>
          <label className="station-link">
            <input type="checkbox" checked={linked} onChange={(event) => setLinked(event.target.checked)} />
            Link the 3D station to the simulator
          </label>
        </div>
        <div className="demo-frames">
          <iframe
            ref={simulator}
            src={simulatorSrc}
            title={demos['/simulator'].frameTitle}
            sandbox="allow-scripts"
            className={active === '/simulator' ? 'demo-frame' : 'demo-frame demo-frame-parked'}
            inert={active !== '/simulator'}
            aria-hidden={active !== '/simulator' || undefined}
          />
          <iframe
            ref={station}
            src={stationSrc}
            title={demos['/station'].frameTitle}
            sandbox="allow-scripts"
            className={active === '/station' ? 'demo-frame' : 'demo-frame demo-frame-parked'}
            inert={active !== '/station'}
            aria-hidden={active !== '/station' || undefined}
          />
        </div>
        <p className="station-note">
          Evidence type: simulation. Readings come from the simulator and are not field measurements. While linked, the 3D
          station uses the simulator’s readings and limits, even when you are viewing the other page. Opened on its own, the 3D
          station uses its own example values and limits.{' '}
          <a href={active === '/simulator' ? simulatorSrc : stationSrc} target="_blank" rel="noopener noreferrer">
            Open this page on its own
          </a>
        </p>
      </section>
      <nav className="page-sequence" aria-label="Prototype reading order">
        <Link className={other === '/station' ? 'next' : undefined} to={other}>
          <span>{other === '/station' ? 'Next' : 'Previous'}</span>
          {demos[other].title}
        </Link>
      </nav>
    </article>
  );
}
