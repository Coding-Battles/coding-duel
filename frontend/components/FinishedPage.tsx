// This file was moved from in-game/finished/page.tsx to [questionId]/finished/page.tsx for dynamic routing.
// You may want to update this file to use the questionId param if needed.

import React from "react";

const FinishedPage = ({}) => {
  return (
    <div className="flex flex-col items-center justify-center h-[100%] w-[100%]">
      <div className="flex-col flex items-center border-2 border-black shadow-xl px-4 pt-2 pb-8 text-xs w-[400px] h-[300px]">
        <p className="text-lg font-bold text-center">Stats</p>
        <div className="flex items-center justify-between w-full mt-8">
          <span></span>
          <b>Time Finished</b>
          <span></span>
        </div>
        <div className="flex items-center justify-between w-full mt-8">
          <span></span>
          <b>Time Complexity</b>
          <span></span>
        </div>
        <div className="flex items-center justify-between w-full mt-8">
          <span></span>
          <b>Total score</b>
          <span></span>
        </div>
      </div>
      <div className="flex gap-4 mt-[100px]">
        <div className="flex flex-col items-center justify-center p-6 border-2 border-green-300 rounded-lg">
          <img
            src=""
            alt="winnerImage"
            className="w-24 h-24 mb-4 border-2 border-gray-300"
          />
          <h1 className="text-2xl font-bold">Winner</h1>
        </div>

        <div className="flex flex-col items-center justify-center p-6 border-2 border-red-300 rounded-lg">
          <img
            src=""
            alt="winnerImage"
            className="w-24 h-24 mb-4 border-2 border-gray-300"
          />
          <h1 className="text-2xl font-bold">Loser</h1>
        </div>
      </div>
      <div className="mt-12">
        <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Go back to main menu
        </button>
      </div>
    </div>
  );
};

export default FinishedPage;
