(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b4cef463b1b1727e.js","sha256":"b4cef463b1b1727ebce639a0215b5df2ee5930c054f3ace95583a1c71cb379d6","count":2140,"publishedAt":"2026-10-15T04:50:40Z","state":"calendar-state.json","stateSha256":"a6e91789b042fd562fb41892772d28f6eeea949ca3207ba9806db735e7e33120","sourceState":"calendar-source-state.json","sourceStateSha256":"8723e44cc1be4a872f99367a96c91feb25013d21e8530b1e69bc69d3ce4138f2"});
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
