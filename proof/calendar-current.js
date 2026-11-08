(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7e4c2aceb1d3400.js","sha256":"e7e4c2aceb1d340083fe1e976b7d0acb5bd24077b6798ae02214b436f8e38377","count":1987,"publishedAt":"2026-11-08T22:15:32Z","state":"calendar-state.json","stateSha256":"e4ceb4ee4c7995a59685e566a209a8416d6919de7ec9b653b8e3d456b96e099d","sourceState":"calendar-source-state.json","sourceStateSha256":"83a0e6439c60d1af785bd6b6fc1259f1802a17ce95263e4867fdce6c33f3ea1f"});
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
