(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.70a488f3ab80ed9d.js","sha256":"70a488f3ab80ed9d23c4543ceb5c1c36c517b6d388f1e7596879323bf1ddbc4f","count":2065,"publishedAt":"2026-10-22T12:02:37Z","state":"calendar-state.json","stateSha256":"13003f9d7f8b252a6b1bdf9b064434869d7e586303d78003c593fc06eed90483","sourceState":"calendar-source-state.json","sourceStateSha256":"9a618cb638c9cdd0be60e4ba12ed5b973f62ed72e78ea87aec0695b6176a2109"});
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
