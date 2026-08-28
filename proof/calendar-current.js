(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ba4d042aee2dacad.js","sha256":"ba4d042aee2dacad1e901a1390bb5f78ddee1cce231ea74f47a8a4decf72d872","count":2072,"publishedAt":"2026-08-28T19:25:05Z","state":"calendar-state.json","stateSha256":"0a82e61d74670bf6f586f2be3b93210b03cb459944c8ec06b58b2170169e1ae7"});
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
