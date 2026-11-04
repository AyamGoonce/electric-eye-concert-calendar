(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ad9c65709290ea62.js","sha256":"ad9c65709290ea62e9d671352dd0f205ddffac56da1009e1c21129680ee7caa2","count":2047,"publishedAt":"2026-11-04T17:21:08Z","state":"calendar-state.json","stateSha256":"debd2cb4eb322046593db317b315c35f8865ddbe8ff235d812f3614a0a1584f5","sourceState":"calendar-source-state.json","sourceStateSha256":"46d54c37df05c9d4103301f66950295a73ad3472aa7bde13be4a0774d4b6105e"});
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
