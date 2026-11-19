import overview from './content/sections/01-project-details';
import background from './content/sections/02-background';
import criteria from './content/sections/03-problem-criteria';
import options from './content/sections/04-design-options';
import design from './content/sections/05-detailed-design';
import prototyping from './content/sections/06-prototyping';
import implementation from './content/sections/07-implementation';
import costs from './content/sections/08-cost-analysis';
import considerations from './content/sections/09-considerations';
import recommendations from './content/sections/10-recommendations';
import references from './content/references';
import appendices from './content/appendices';
import type { ReportSection } from './content/types';

export const reportRoutes: readonly { path: string; section: ReportSection }[] = [
  { path: '/', section: overview },
  { path: '/pages/background', section: background },
  { path: '/pages/problem-criteria', section: criteria },
  { path: '/pages/design-options', section: options },
  { path: '/pages/detailed-design', section: design },
  { path: '/pages/prototyping', section: prototyping },
  { path: '/pages/implementation', section: implementation },
  { path: '/pages/cost-analysis', section: costs },
  { path: '/pages/considerations', section: considerations },
  { path: '/pages/recommendations', section: recommendations },
  { path: '/pages/references', section: references },
  { path: '/pages/appendices', section: appendices },
];
