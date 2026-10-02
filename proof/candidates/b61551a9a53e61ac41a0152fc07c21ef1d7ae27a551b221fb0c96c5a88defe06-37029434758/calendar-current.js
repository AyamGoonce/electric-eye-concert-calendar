(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b61551a9a53e61ac.js","sha256":"b61551a9a53e61ac41a0152fc07c21ef1d7ae27a551b221fb0c96c5a88defe06","count":2222,"publishedAt":"2026-10-02T15:47:52Z","state":"calendar-state.json","stateSha256":"4e6171a4add3333609359d1aafd4eba9fd751a491dd3175b37815817e82fa738","sourceState":"calendar-source-state.json","sourceStateSha256":"eba9a4828f132091e32af9a60861031c4ac5ba98be41b3ed2edffd1bfcc74aa4"});
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
