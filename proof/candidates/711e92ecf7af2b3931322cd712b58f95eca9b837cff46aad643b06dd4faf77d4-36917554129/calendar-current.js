(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.711e92ecf7af2b39.js","sha256":"711e92ecf7af2b3931322cd712b58f95eca9b837cff46aad643b06dd4faf77d4","count":2224,"publishedAt":"2026-10-01T19:53:59Z","state":"calendar-state.json","stateSha256":"33c6f53c6df34b3f641a5bc41ed1ff50e295f3ced42b5772b12edbb22bf10840","sourceState":"calendar-source-state.json","sourceStateSha256":"aeeebe57db2687c02c284e3c59ea060df20984ea1ebe07dfa6a7ac91c5333311"});
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
