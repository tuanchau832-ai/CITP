import { Link } from 'react-router';
import type { StationDemoData } from '../content/types';

/** Points the reader to the two linked prototype pages: the sensor simulator and the 3D station. */
export function StationDemo({ id, caption, simulatorPath, stationPath, note }: StationDemoData) {
  return (
    <figure id={id} className="station-demo">
      <ul className="station-demo-links">
        <li><Link to={simulatorPath}>Open the sensor simulator</Link></li>
        <li><Link to={stationPath}>Open the 3D station</Link></li>
      </ul>
      <figcaption>{caption}</figcaption>
      {note && <p className="station-note">{note}</p>}
    </figure>
  );
}
