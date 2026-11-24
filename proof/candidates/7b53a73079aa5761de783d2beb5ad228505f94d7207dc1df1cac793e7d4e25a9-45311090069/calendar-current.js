(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b53a73079aa5761.js","sha256":"7b53a73079aa5761de783d2beb5ad228505f94d7207dc1df1cac793e7d4e25a9","count":2096,"publishedAt":"2026-11-24T02:16:18Z","state":"calendar-state.json","stateSha256":"7b4dd0e0ff4c6814704973bf35263839c054edb0eaa11e64026da3e85874b474","sourceState":"calendar-source-state.json","sourceStateSha256":"7bbfb08b8ed50e6fda288fe677def2a026b8a71c3582870cc8a30c3ee0ca0fb4"});
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
