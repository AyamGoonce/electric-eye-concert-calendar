(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.df207479d67e97e9.js","sha256":"df207479d67e97e92ddbbeea9f3ca552c3bc2e7ba852a3816056abd8c4733f91","count":2104,"publishedAt":"2026-11-26T00:40:54Z","state":"calendar-state.json","stateSha256":"ccb56ca62c174885b9aae02544ab444b5d94bb2d4deaa118135741be7aa7b9b9","sourceState":"calendar-source-state.json","sourceStateSha256":"884d7fa6cdb1cbe833a1587a3c3d33561eb276479cc661964fa80be4cfc26b33"});
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
