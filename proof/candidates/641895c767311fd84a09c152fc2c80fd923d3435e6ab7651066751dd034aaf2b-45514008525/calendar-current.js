(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.641895c767311fd8.js","sha256":"641895c767311fd84a09c152fc2c80fd923d3435e6ab7651066751dd034aaf2b","count":2101,"publishedAt":"2026-11-24T23:56:02Z","state":"calendar-state.json","stateSha256":"d51c20472d7effcde883ca8ae44eb84425fad7d989cbc847fa3486bb15e066a9","sourceState":"calendar-source-state.json","sourceStateSha256":"6a470cac4295b3c36e46dda03aa8b62a89dcb625e73496303557f29ff630d1d8"});
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
