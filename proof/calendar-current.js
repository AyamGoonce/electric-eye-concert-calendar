(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.545b257f17e3b038.js","sha256":"545b257f17e3b03805c37498611d5dbcee7e1fc1569e8f434ccc464e482f590f","count":2218,"publishedAt":"2026-10-01T00:35:57Z","state":"calendar-state.json","stateSha256":"ee0ffb82361d4c62af86b47adcf47696830f24c7f8f25f8648b2599c507f07c2","sourceState":"calendar-source-state.json","sourceStateSha256":"c9da334c304c213de346ba8c9931bcc32b4d6199fe89e748f1e20bf8b69f12aa"});
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
