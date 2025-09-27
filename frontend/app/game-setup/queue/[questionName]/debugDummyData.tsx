import { TestResultsData } from "@/components/TestResults";
import { CustomUser } from "@/shared/schemas";
import { OpponentData } from "@/shared/types";

// Dummy data - User wins scenario
export const dummyUserWinsData = {
  opponent: {
    image_url:
      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    name: "Alex Thompson",
  } as OpponentData,

  user: {
    id: "user123",
    name: "John Doe",
    email: "john@example.com",
  } as CustomUser,

  opponentStats: {
    player_name: "Alex Thompson",
    implement_time: 165, // Changed from "2:45" to a number (e.g., seconds)
    complexity: "O(n²)",
    final_time: 165.8,
    success: true,
    test_results: [],
    total_passed: 0,
    total_failed: 0,
    error: "",
    message: "",
    code: "",
    opponent_id: "opponent123",
  } as TestResultsData,

  userStats: {
    player_name: "John Doe",
    implement_time: 132, // Changed from "2:12" (string) to 132 (number, e.g., seconds)
    complexity: "O(n log n)",
    final_time: 132.5,
    success: true,
    test_results: [],
    total_passed: 0,
    total_failed: 0,
    error: "",
    message: "",
    code: "",
    opponent_id: "",
  } as TestResultsData,

  gameEndData: {
    winner_id: "user123",
    loser_id: "opponent123",
    winner_name: "John Doe",
    loser_name: "Alex Thompson",
    winner_avatar_url:
      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    loser_avatar_url:
      "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    question_name: "Two Sum Problem",
    lp_gained: 15,
    lp_loss: 10,
    game_end_reason: "Completed",
  } as any
};