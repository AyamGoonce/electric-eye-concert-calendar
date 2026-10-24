(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.eda5977f3c988637.js","sha256":"eda5977f3c988637c898fe502812a952c5275545050a5b5877431588084c422f","count":2079,"publishedAt":"2026-10-24T11:13:08Z","state":"calendar-state.json","stateSha256":"7c62367a682008444c865d64711f43bff85fb1247ccf0a7c25045e354d97c3f8","sourceState":"calendar-source-state.json","sourceStateSha256":"9ec1c09098f4f7c1f34204591adf803988284ee0bc3d36800fc7a6ffa2615a34"});
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
