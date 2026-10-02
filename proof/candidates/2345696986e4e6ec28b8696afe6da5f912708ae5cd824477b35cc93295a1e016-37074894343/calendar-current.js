(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2345696986e4e6ec.js","sha256":"2345696986e4e6ec28b8696afe6da5f912708ae5cd824477b35cc93295a1e016","count":2219,"publishedAt":"2026-10-02T22:54:23Z","state":"calendar-state.json","stateSha256":"db3c2333a2e987ea8a5487103b6b3314a3586f9072612d4a6f9e924e8dc1ad18","sourceState":"calendar-source-state.json","sourceStateSha256":"3f7a02c5f8aadfa813012eac57d507c1e393a168365b400a201768c51a51c896"});
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
