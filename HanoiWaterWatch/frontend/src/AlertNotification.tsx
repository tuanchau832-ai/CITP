import { useEffect, useRef, useState } from 'react';
import { Bell, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useText } from './common';
import type { Alert } from './types';

export function AlertNotification({ alerts }: { alerts?: Alert[] }) {
  const { t } = useTranslation();
  const text = useText();
  const seen = useRef<number | undefined>(undefined);
  const [notification, setNotification] = useState<Alert>();

  useEffect(() => {
    if (!alerts) return;
    const newest = alerts.reduce<Alert | undefined>((latest, alert) =>
      !latest || alert.id > latest.id ? alert : latest, undefined);
    if (newest && seen.current !== undefined && newest.id > seen.current) {
      setNotification(newest);
    }
    seen.current = Math.max(seen.current ?? 0, newest?.id ?? 0);
  }, [alerts]);

  if (!notification) return null;
  return (
    <aside className="alert-notification" aria-label={t('newPreliminaryAlert')}>
      <Bell size={18} aria-hidden="true" />
      <div>
        <div role="status">
          <strong>{t('newPreliminaryAlert')}</strong>
          <p>{notification.station_code} · {text(notification.rule_name)}</p>
        </div>
        <Link className="textlink" to={`/alerts/${notification.id}`} onClick={() => setNotification(undefined)}>
          {t('reviewAlertLink')}
        </Link>
      </div>
      <button className="icon-button" aria-label={t('dismissNotification')} onClick={() => setNotification(undefined)}>
        <X size={16} />
      </button>
    </aside>
  );
}
