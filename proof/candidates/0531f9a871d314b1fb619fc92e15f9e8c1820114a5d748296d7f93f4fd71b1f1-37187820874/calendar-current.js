(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0531f9a871d314b1.js","sha256":"0531f9a871d314b1fb619fc92e15f9e8c1820114a5d748296d7f93f4fd71b1f1","count":2182,"publishedAt":"2026-10-04T08:08:05Z","state":"calendar-state.json","stateSha256":"46709fe54ebaaae16518f15b586fa33dd9ada207dd3fc0a5e84f258af41e1e31","sourceState":"calendar-source-state.json","sourceStateSha256":"51e7891fa7a50cd311f223867153ff539b435b72674c57d254afaa133425c482"});
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
