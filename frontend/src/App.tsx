import { useRef, useState } from "react";
import EmberBackground from "./components/EmberBackground";
import Hero from "./components/Hero";
import GoalStage from "./components/GoalStage";
import BallLayer from "./components/BallLayer";
import ChatPanel from "./components/ChatPanel";
import type { ShotState } from "./components/shot";

export default function App() {
  const [shot, setShot] = useState<ShotState>("idle");
  const [shotId, setShotId] = useState(0);
  const stageRef = useRef<HTMLDivElement>(null);

  const onShot = (s: ShotState) => {
    if (s === "thinking") setShotId((n) => n + 1);
    setShot(s);
  };

  return (
    <>
      <EmberBackground />
      <div style={{ position: "relative", zIndex: 1 }}>
        <Hero />
        <main>
          <GoalStage ref={stageRef} state={shot} shotId={shotId}>
            <ChatPanel shot={shot} onShot={onShot} />
          </GoalStage>
        </main>
      </div>
      <BallLayer state={shot} shotId={shotId} stageRef={stageRef} />
    </>
  );
}
