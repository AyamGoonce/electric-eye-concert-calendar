(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c4d99564154819ac.js","sha256":"c4d99564154819ac3dd716ab3d77096d660b740fc7eb20265555b2137bbe9bfa","count":2052,"publishedAt":"2026-10-27T15:31:09Z","state":"calendar-state.json","stateSha256":"a496c728503e21982e11ebb290ee7925b9831ee286937b5f747b3cef51bed551","sourceState":"calendar-source-state.json","sourceStateSha256":"ca1cf0204f8a28afe28f51a527cf071e4a466040ca50191bb8db7c5c874ce9f5"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
