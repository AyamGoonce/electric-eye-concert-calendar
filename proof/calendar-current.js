(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f67a8c43251b951d.js","sha256":"f67a8c43251b951dff367b2fcbc2cb0ec6fe8395b8453c1fdbdbad032c67e4ba","count":2134,"publishedAt":"2026-09-25T10:38:40Z","state":"calendar-state.json","stateSha256":"cf16a3eb5e0b47e5c9e54d7eda5abe4ce4103e95fd48cc9f2590f2727f077b0a","sourceState":"calendar-source-state.json","sourceStateSha256":"e187ae781a25328aa9833d5bad6ec988768aff123dfc96a71a5c9c155b82365e"});
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
