import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { AnimatePresence, motion, HTMLMotionProps } from "framer-motion";

import { cn } from "@/lib/utils";
import { AlertTriangle } from "lucide-react";

const alertVariants = cva(
  "relative w-full rounded-lg border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground",
        destructive:
          "text-destructive bg-card [&>svg]:text-current *:data-[slot=alert-description]:text-destructive/90",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Alert({
  className,
  variant,
  id,
  setAlerts,
  ...props
}: HTMLMotionProps<"div"> &
  VariantProps<typeof alertVariants> & {
    id: string;
    setAlerts?: React.Dispatch<React.SetStateAction<AlertType[]>>;
  }) {
  const [show, setShow] = React.useState(true);
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setShow(false);
      if (setAlerts) {
        setAlerts((prev) => prev.filter((alert) => alert.id !== id));
      }
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          data-slot="alert"
          role="alert"
          className={cn(alertVariants({ variant }), className)}
          {...props}
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.5 }}
        />
      )}
    </AnimatePresence>
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-title"
      className={cn(
        "col-start-2 line-clamp-1 min-h-4 font-medium tracking-tight",
        className
      )}
      {...props}
    />
  );
}

function AlertDescription({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn(
        "text-muted-foreground col-start-2 grid justify-items-start gap-1 text-sm [&_p]:leading-relaxed",
        className
      )}
      {...props}
    />
  );
}
type AlertType = { id: string; message: string; variant?: string };
function StackableAlerts({
  alerts,
  setAlerts,
  className,
}: {
  alerts: AlertType[];
  setAlerts: React.Dispatch<React.SetStateAction<AlertType[]>>;
  className?: string;
}) {
  return (
    <AnimatePresence>
      {alerts.map((alert, key) => (
        <motion.div
          key={key}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="absolute right-4 top-[4rem] w-[300px] z-50"
          style={{ top: `${4 + key * 6}rem` }}
        >
          <Alert id={alert.id} setAlerts={setAlerts}>
            <AlertTriangle className="text-error" />
            <AlertTitle>Heads up!</AlertTitle>
            <AlertDescription>{alert.message}</AlertDescription>
          </Alert>
        </motion.div>
      ))}
    </AnimatePresence>
  );
}

export { Alert, AlertTitle, AlertDescription, StackableAlerts };
