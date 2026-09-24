(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a95038feaccbab2d.js","sha256":"a95038feaccbab2d24885fb38cc9e4e4099f2dbf91132cfa90f93e8647f46d78","count":2128,"publishedAt":"2026-09-24T04:59:09Z","state":"calendar-state.json","stateSha256":"faef3cb019e5aaf1f3d3b296779ec790b1dd38a75f6dd6488b6780b837024988","sourceState":"calendar-source-state.json","sourceStateSha256":"9bca77f176758fc1244e555104d9af2ba6a06ae64ac80fdba858cf1f0564dd37"});
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
